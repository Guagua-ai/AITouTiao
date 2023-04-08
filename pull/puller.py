import time
import openai
import urllib.parse
from models.tweet import Tweet
from config.config import TweetConfig
from db.conn import get_connection
from sqlalchemy.exc import IntegrityError
import snscrape.modules.twitter as sntwitter


class Puller:
    ''' Puller class '''

    def __init__(self, api_key, local=False):
        assert api_key, 'Please provide an OpenAI API key'
        openai.api_key = api_key
        self.config = TweetConfig()
        self.local = local

    # get tweets from a user
    def get_tweets(self, username, max_results):
        tweet_list = []
        for i, tweet in enumerate(sntwitter.TwitterUserScraper(username).get_items()):
            if i >= max_results:
                break

            # Use inReplyToTweetId instead of inReplyToStatusId
            if not tweet.inReplyToTweetId and '@' not in tweet.rawContent:
                try:
                    url = urllib.parse.urlparse(tweet.rawContent)
                    if not (url.scheme and url.netloc):
                        tweet_list.append(tweet)
                except ValueError:
                    tweet_list.append(tweet)

        return tweet_list

    # translate text to chinese
    def translate_to_chinese(self, text):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Translate the following English text to Simplified Chinese: '{text}'",
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.4,
        )

        translation = response.choices[0].text.strip()
        return translation

    # retrieve tweets of users
    def retrieveTweetsOfUsers(self, usernames, all_tweets):
        for username in usernames:
            print(f"Fetching tweets from {username}")
            tweets = self.get_tweets(username, self.config.max_results)

            formatted_tweets = []
            for tweet in tweets:
                url = f"https://twitter.com/{tweet.user.username}/status/{tweet.id}"
                # check if tweet already exists
                if Tweet.get_tweet_by_url(url):
                    continue
                content = self.translate_to_chinese(tweet.rawContent)
                title = content
                if len(content) > 20:
                    title = content[:20]
                description = content
                if len(content) > 40:
                    description = content[:40] + '...'
                formatted_tweet = {
                    'source': {
                        'id': tweet.user.id,
                        'name': "Twitter",
                    },
                    'author': tweet.user.username,
                    'title': title,
                    'description': description,
                    'url': url,
                    'urlToImage': tweet.user.profileImageUrl,
                    'publishedAt': tweet.date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'content': content,
                }
                formatted_tweets.append(formatted_tweet)
            all_tweets.extend(formatted_tweets)
        return formatted_tweets

    # run the puller
    def run(self):
        start_time = time.time()

        usernames = ['elonmusk', 'sama', 'ylecun']

        # more_usernames = ['OpenAI', 'DeepMind', 'demishassabis',
        #                   'goodfellow_ian', 'ylecun', 'karpathy']

        all_tweets = []
        formatted_tweets = self.retrieveTweetsOfUsers(usernames, all_tweets)

        if self.local:
            import pandas as pd
            df = pd.DataFrame(formatted_tweets)
            df.to_csv('ai_tweets_translated.csv', index=False)
        else:
            session = get_connection()
            for tweet in formatted_tweets:
                new_tweet = Tweet(
                    source_id=tweet['source']['id'],
                    source_name=tweet['source']['name'],
                    author=tweet['author'],
                    title=tweet['title'],
                    description=tweet['description'],
                    url=tweet['url'],
                    url_to_image=tweet['urlToImage'],
                    published_at=tweet['publishedAt'],
                    content=tweet['content'],
                )
                session.add(new_tweet)
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    print(f"Duplicate URL found: {tweet['url']}")
            session.close()

        elapsed_time = time.time() - start_time
        if self.local:
            print(
                f"Saved results to ai_tweets_translated.csv in {elapsed_time:.2f} seconds")
        else:
            print(f"Saved results to database in {elapsed_time:.2f} seconds")
