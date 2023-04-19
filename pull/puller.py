import os
import time
from flask import Flask
import openai
import urllib.parse

import requests
from db.conn import db, get_connection
from db.storage import check_if_object_exists_on_s3, upload_image_to_s3
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
            image_set = set()
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

                    url_to_image = self.process_image(tweet, image_set)
                    formatted_tweet = {
                        'source': {
                            'id': tweet.user.id,
                            'name': "Twitter",
                        },
                        'author': tweet.user.username,
                        "displayname": tweet.user.displayname,
                        'title': title,
                        'description': description,
                        'url': url,
                        'urlToImage': url_to_image,
                        'publishedAt': tweet.date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'content': content,
                    }
                    formatted_tweets.append(formatted_tweet)
                all_tweets.extend(formatted_tweets)
        return all_tweets
    
    def process_image(self, tweet, image_set):
        if not tweet.user.profileImageUrl:
            return tweet.user.profileImageUrl

        if tweet.user.profileImageUrl in image_set:
            return tweet.user.profileImageUrl

        # Check if image is already in S3
        if "s3.amazonaws.com" in tweet.user.profileImageUrl:
            return tweet.user.profileImageUrl

        # Get the bucket key and object key
        bucket_key = 'server-news-tweet-photo'
        object_key = f'tweets/{tweet.user.username}.jpg'

        # Get the URL of the S3 object
        object_url = f'https://{bucket_key}.s3.amazonaws.com/{object_key}'

        # Check if image is already in S3
        if check_if_object_exists_on_s3(bucket_key, object_key):
            return object_url

        # Download image from URL
        response = requests.get(tweet.user.profileImageUrl)
        if response.status_code != 200:
            return tweet.user.profileImageUrl
        image_data = response.content

        # Upload image to S3
        bucket_key = 'server-news-tweet-photo'
        success = upload_image_to_s3(bucket_key, object_key, image_data)
        if not success:
            return tweet.user.profileImageUrl

        # Add image to image_set
        image_set.add(tweet.user.profileImageUrl)
        return object_url

    # store tweets to database
    def store_tweets_to_database(self, session, tweet):
        new_tweet = Tweet(
                    source_id=tweet['source']['id'],
                    source_name=tweet['source']['name'],
                    author=tweet['author'],
                    display_name=tweet['displayname'],
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
    
    def download_tweet_image(self, tweet) -> str:
        if not tweet.url_to_image:
            return tweet.url_to_image
        # download image
        if "s3.amazonaws.com" in tweet.url_to_image:
            return tweet.url_to_image

        if db.check_if_object_exists(tweet.url_to_image):
            return tweet.url_to_image

        return tweet

    # run the puller
    def run(self, usernames=[]):
        start_time = time.time()

        if not usernames:
            usernames = ['elonmusk', 'sama', 'ylecun']

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