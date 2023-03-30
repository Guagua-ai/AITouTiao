import time
import snscrape.modules.twitter as sntwitter
import csv
import openai
import urllib.parse

openai.api_key = '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'


def get_tweets(username, max_results):
    tweet_data = []
    for i, tweet in enumerate(sntwitter.TwitterUserScraper(username).get_items()):
        if i >= max_results:
            break

        # Use inReplyToTweetId instead of inReplyToStatusId
        if not tweet.inReplyToTweetId and '@' not in tweet.rawContent:
            try:
                url = urllib.parse.urlparse(tweet.rawContent)
                if not (url.scheme and url.netloc):
                    tweet_data.append((tweet.url, tweet.rawContent))
            except ValueError:
                tweet_data.append((tweet.url, tweet.rawContent))

    return tweet_data


def translate_to_chinese(text):
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


start_time = time.time()

username = 'elonmusk'
max_results = 100
tweets = get_tweets(username, max_results)

with open('elonmusk_tweets_translated.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(
        ['Username', 'Tweet URL', 'Tweet Text', 'Translated Text'])

    for tweet_url, tweet_text in tweets:
        translated_text = translate_to_chinese(tweet_text)
        csv_writer.writerow([username, tweet_url, tweet_text, translated_text])

elapsed_time = time.time() - start_time
print(
    f"Saved results to elonmusk_tweets_translated.csv in {elapsed_time:.2f} seconds")
