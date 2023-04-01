import time
import snscrape.modules.twitter as sntwitter
import openai
import urllib.parse


class Puller:
    def __init__(self, api_key, local=False):
        assert api_key, 'Please provide an OpenAI API key'
        openai.api_key = api_key
        self.local = local

    def get_tweets(self, username, max_results):
        tweet_list = []
        for i, tweet in enumerate(sntwitter.TwitterUserScraper(username).get_items()):
            if i >= max_results:
                break

            # Use inReplyToTweetId instead of inReplyToStatusId
            if not tweet.inReplyToTweetId and '@' not in tweet.content:
                try:
                    url = urllib.parse.urlparse(tweet.content)
                    if not (url.scheme and url.netloc):
                        tweet_list.append(tweet)
                except ValueError:
                    tweet_list.append(tweet)

        return tweet_list

    def translate_to_chinese(self, text):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Translate the following English text to Chinese: '{text}'",
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.8,
        )

        translation = response.choices[0].text.strip()
        return translation

    def run(self):
        start_time = time.time()

        username = 'elonmusk'
        max_results = 100
        tweets = self.get_tweets(username, max_results)

        formatted_tweets = []
        for tweet in tweets:
            formatted_tweet = {
                'source': {
                    'id': tweet.user.id,
                    'name': "Twitter",
                },
                'author': tweet.user.username,
                'title': self.translate_to_chinese(tweet.content),
                'description': '',  # Description is not available in Tweet object
                'url': f"https://twitter.com/{tweet.user.username}/status/{tweet.id}",
                'urlToImage': tweet.user.profileImageUrl,
                'publishedAt': tweet.date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'content': self.translate_to_chinese(tweet.content)
            }
            formatted_tweets.append(formatted_tweet)

        if self.local:
            import pandas as pd
            df = pd.DataFrame(formatted_tweets)
            df.to_csv('elonmusk_tweets_translated.csv', index=False)

        elapsed_time = time.time() - start_time
        print(
            f"Saved results to elonmusk_tweets_translated.csv in {elapsed_time:.2f} seconds")
