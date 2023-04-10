import os
import time
from flask import Flask
import openai
import urllib.parse
from db.conn import db, get_connection
from search import create_post_search_index
from sqlalchemy.exc import IntegrityError
from models.tweet import Tweet
from config.tweet import TweetConfig
import snscrape.modules.twitter as sntwitter


class Puller(object):
    ''' Puller class '''

    def __init__(self, api_key, translator=None, local=False):
        assert api_key, 'Please provide an OpenAI API key'
        openai.api_key = api_key
        self.config = TweetConfig()
        self.translator = translator
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

    # retrieve tweets of users
    def retrieve_tweets_of_users(self, usernames):
        all_tweets = []
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') + '/news_dev'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        with app.app_context():
            for username in usernames:
                print(f"Fetching tweets from {username}")
                tweets = self.get_tweets(username, self.config.max_results)

                formatted_tweets = []
                for tweet in tweets:
                    url = f"https://twitter.com/{tweet.user.username}/status/{tweet.id}"
                    # check if tweet already exists
                    if Tweet.get_tweet_by_url(url):
                        continue
                    if not self.translator.is_related_to_ai(tweet.rawContent):
                        continue
                    # generate chinese news feed post
                    title, content = self.translator.generate_chinese_news_feed_post(
                        tweet.user.displayname,
                        tweet.rawContent)
                    if not title or not content:
                        continue
                    # save tweet to db
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
        return all_tweets
    
    # store tweets to database
    def store_tweets_to_database(self, session, tweet):
        new_tweet = Tweet(
                    source_id=tweet['source']['id'],
                    source_name=tweet['source']['name'],
                    author=tweet['author'],
                    title=tweet['title'],
                    description=tweet['description'],
                    url=tweet['url'],
                    url_to_image=tweet['urlToImage'],
                    published_at=tweet['publishedAt'],
                    created_at=time.strftime('%Y-%m-%d %H:%M:%S'),
                    content=tweet['content'],
                )
        session.add(new_tweet)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            print(f"Duplicate URL found: {tweet['url']}")
        return new_tweet

    # create search index
    def create_search_index(new_tweet):
        return ({
            "objectID": new_tweet.id,
            "author": new_tweet.author,
            "title": new_tweet.title,
            "description": new_tweet.description,
            "url": new_tweet.url,
            "url_to_image": new_tweet.url_to_image,
            "published_at": new_tweet.published_at,
            "content": new_tweet.content,
        })
    
    # run the puller
    def run(self, usernames=[]):
        start_time = time.time()

        if not usernames:
            usernames = ['elonmusk', 'sama', 'ylecun']

        # more_usernames = ['OpenAI', 'DeepMind', 'demishassabis',
        #                   'goodfellow_ian', 'ylecun', 'karpathy']

        all_tweets = self.retrieve_tweets_of_users(usernames)
        all_tweets_indices = []
        
        if self.local:
            import pandas as pd
            df = pd.DataFrame(all_tweets)
            df.to_csv('ai_tweets_translated.csv', index=False)
        else:
            session = get_connection()
            for tweet in all_tweets:
                new_tweet = self.store_tweets_to_database(session, tweet)
                # create search index
                all_tweets_indices.append(Puller.create_search_index(new_tweet))
            session.close()

        # save to algolia in batches
        create_post_search_index().save_objects(all_tweets_indices)

        elapsed_time = time.time() - start_time
        if self.local:
            print(
                f"Saved results to ai_tweets_translated.csv in {elapsed_time:.2f} seconds")
        else:
            print(f"Saved results to database in {elapsed_time:.2f} seconds")