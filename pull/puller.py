import os
import time
import openai
import requests
import urllib.parse
import snscrape.modules.twitter as sntwitter

from flask import Flask
from db.conn import db, get_connection
from db.storage import check_if_object_exists_on_s3, upload_image_to_s3
from sqlalchemy.exc import IntegrityError
from search.index import create_internal_post_search_index
from models.tweet import Tweet
from models.twitter_user import TwitterUser
from config.tweet import TweetConfig
from tenacity import retry, wait_exponential, stop_after_attempt


class Puller(object):
    ''' Puller class '''

    def __init__(self, api_key, translator=None):
        assert api_key, 'Please provide an OpenAI API key'
        openai.api_key = api_key
        self.config = TweetConfig()
        self.translator = translator

        # Add Twitter API credentials
        self.version = 1
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    # pull tweets from twitter
    @retry(wait=wait_exponential(multiplier=1, min=2, max=60), stop=stop_after_attempt(5))
    def get_tweets_v2(self, username, max_results):
        tweet_list = []
        headers = {"Authorization": f"Bearer {self.twitter_bearer_token}"}
        user_id = self.get_user_id(username, headers)

        if not user_id:
            return tweet_list

        url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results={max_results}&tweet.fields=created_at,public_metrics,entities&expansions=author_id&user.fields=username,profile_image_url,name"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error fetching tweets for {username}: {response.text}")
            raise Exception(
                f"Error fetching tweets for {username}: {response.text}")

        return response.json()  # Return the raw JSON response

    # get user id from username
    def get_user_id(self, username, headers):
        twitter_user = TwitterUser.get_user_by_username(username)
        if twitter_user:
            return twitter_user.user_id

        url = f"https://api.twitter.com/2/users/by/username/{username}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error fetching user ID for {username}: {response.text}")
            return None

        user_data = response.json()
        twitter_user = TwitterUser.create_user(
            user_id=user_data['data']['id'], username=username)
        if twitter_user is None:
            raise Exception(f"Error creating user {username}")

        print(user_data)
        return user_data['data']['id']

    # retrieve tweets of users
    def retrieve_tweets_of_users_v2(self, usernames):
        all_tweets = []
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL') + '/news_dev'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        with app.app_context():
            image_set = set()
            for username in usernames:
                print(f"Fetching tweets from {username}")
                tweets_data = self.get_tweets_v2(
                    username, self.config.max_results)

                formatted_tweets = []
                for raw_tweet in tweets_data['data']:
                    print(raw_tweet)
                    url = f"https://twitter.com/{raw_tweet['author_id']}/status/{raw_tweet['id']}"

                    # check if tweet already exists
                    if Tweet.get_tweet_by_url(url):
                        continue

                    # check if tweet is related to AI
                    # if not self.translator.is_related_to_ai(raw_tweet['text']):
                    #     continue

                    # check if twitter user needs update
                    author_name, author_username, profile_url = self.store_twitter_user_v2(
                        username, tweets_data, raw_tweet)

                    try:
                        # generate chinese news feed post
                        title, content = self.translator.generate_chinese_news_feed_post(
                            author_name,
                            raw_tweet['text'])
                    except Exception as e:
                        print(e)
                        continue
                    if not title or not content:
                        continue

                    # save tweet to db
                    description = content
                    if len(content) > 40:
                        description = content[:40] + '...'

                    # process image if needed
                    url_to_image = self.process_image(
                        username=author_username,
                        profile_image_url=profile_url,
                        image_set=image_set)

                    formatted_tweet = {
                        'source': {
                            'id': raw_tweet['author_id'],
                            'name': "Twitter",
                        },
                        'author': author_username,
                        'displayname': author_name,
                        'title': title,
                        'description': description,
                        'url': url,
                        'urlToImage': url_to_image,
                        'publishedAt': raw_tweet['created_at'],
                        'content': content,
                        'rawContent': raw_tweet['text'],
                    }

                    formatted_tweets.append(formatted_tweet)
                all_tweets.extend(formatted_tweets)
        return all_tweets
    
    def store_twitter_user(self, username, tweet, image_set):
        twitter_user = TwitterUser.get_user_by_username(username)
        if twitter_user is not None:
            return twitter_user.display_name, twitter_user.username, twitter_user.profile_image_url
        
        author_name = tweet.user.displayname
        author_username = username
    
        # Get a high-resolution profile image
        profile_url = tweet.user.profileImageUrl.replace('_normal', '')
        
                    
        # check if twitter user needs update
        url_to_image = self.process_image(
            username=author_username, 
            profile_image_url=profile_url, 
            image_set=image_set)
        
        # Create a new Twitter user
        twitter_user = TwitterUser.create_user(user_id=tweet.user.id,
                                               username=author_username, 
                                               display_name=author_name, 
                                               profile_image_url=url_to_image)
        if not twitter_user:
            raise Exception(
                f"Error updating user {author_username}")

        return twitter_user.display_name, twitter_user.username, twitter_user.profile_image_url

    # create twitter user
    def store_twitter_user_v2(self, username, tweets_data, raw_tweet):
        twitter_user = TwitterUser.get_user_by_username(username)
        if twitter_user is None:
            raise Exception(
                f"Could not find Twitter User {username}")
        if twitter_user.check_if_needs_update():
            user = next(
                user for user in tweets_data['includes']['users'] if user['id'] == raw_tweet['author_id'])
            author_name = user['name']
            author_username = user['username']
        
            # Get a high-resolution profile image
            profile_url = user['profile_image_url'].replace('_normal', '')
            
            twitter_user = TwitterUser.update(username=author_username, display_name=author_name, profile_image_url=profile_url)
            if not twitter_user:
                raise Exception(
                    f"Error updating user {author_username}")

        return twitter_user.display_name, twitter_user.username, twitter_user.profile_image_url

    # get tweets from a user
    def get_tweets(self, username, max_results):
        tweet_list = []
        for i, tweet in enumerate(sntwitter.TwitterProfileScraper(username).get_items()):
            print(tweet)
            if i >= max_results:
                break
            
            try:
                # Use inReplyToTweetId instead of inReplyToStatusId
                if not tweet.inReplyToTweetId and '@' not in tweet.rawContent:
                    try:
                        url = urllib.parse.urlparse(tweet.rawContent)
                        if not (url.scheme and url.netloc):
                            tweet_list.append(tweet)
                    except ValueError:
                        tweet_list.append(tweet)
            except AttributeError:
                continue

        return tweet_list

    # retrieve tweets of users
    def retrieve_tweets_of_users(self, usernames):
        all_tweets = []
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL') + '/news_dev'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        with app.app_context():
            image_set = set()
            for username in usernames:
                print(f"Fetching tweets from {username}")
                tweets_data = self.get_tweets(username, self.config.max_results)

                formatted_tweets = []
                for tweet in tweets_data:
                    url = f"https://twitter.com/{tweet.user.username}/status/{tweet.id}"

                    # check if tweet already exists
                    if Tweet.get_tweet_by_url(url):
                        continue

                    # check if tweet is related to AI
                    # if not self.translator.is_related_to_ai(tweet.rawContent):
                    #     continue

                    # check if twitter user needs update
                    author_name, author_username, profile_url = self.store_twitter_user(
                        username, tweet, image_set)

                    try:
                        # generate chinese news feed post
                        title, content = self.translator.generate_chinese_news_feed_post(
                            tweet.user.displayname,
                            tweet.rawContent)
                    except Exception as e:
                        print(e)
                        continue
                    
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
                        'author': author_username,
                        "displayname": author_name,
                        'title': title,
                        'description': description,
                        'url': url,
                        'urlToImage': profile_url,
                        'publishedAt': tweet.date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'content': content,
                        'rawContent': tweet.rawContent,
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
            display_name=tweet['displayname'],
            title=tweet['title'],
            description=tweet['description'],
            url=tweet['url'],
            url_to_image=tweet['urlToImage'],
            published_at=tweet['publishedAt'],
            created_at=time.strftime('%Y-%m-%d %H:%M:%S'),
            content=tweet['content'],
            raw_content=tweet['rawContent'],
        )
        session.add(new_tweet)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            print(f"Duplicate URL found: {tweet['url']}")
        return new_tweet

    # process image if needed
    def process_image(self, username, profile_image_url, image_set):
        # Check if image is already in S3
        if not profile_image_url:
            return profile_image_url

        # Check if image is already in S3
        if profile_image_url in image_set:
            return profile_image_url

        # Check if image is already in S3
        if "s3.amazonaws.com" in profile_image_url:
            return profile_image_url

        # Get the bucket key and object key
        bucket_key = 'server-news-tweet-photo'
        object_key = f'tweets/{username}.jpg'

        # Get the URL of the S3 object
        object_url = f'https://{bucket_key}.s3.amazonaws.com/{object_key}'

        # Check if image is already in S3
        if check_if_object_exists_on_s3(bucket_key, object_key):
            return object_url

        # Download image from URL
        response = requests.get(profile_image_url)
        if response.status_code != 200:
            return profile_image_url
        image_data = response.content

        # Upload image to S3
        bucket_key = 'server-news-tweet-photo'
        success = upload_image_to_s3(bucket_key, object_key, image_data)
        if not success:
            return profile_image_url

        # Add image to image_set
        image_set.add(profile_image_url)
        return object_url

    # download tweet image
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

        all_tweets = []
        if self.version == 1:
            all_tweets = self.retrieve_tweets_of_users(usernames)
        else:
            all_tweets = self.retrieve_tweets_of_users_v2(usernames)
        
        all_tweets_indices = []
        session = get_connection()
        for tweet in all_tweets:
            new_tweet = self.store_tweets_to_database(session, tweet)
            
            # create search index
            all_tweets_indices.append(new_tweet.to_index_dict())
            print(f"Stored tweet {new_tweet} to database")
        session.close()

        create_internal_post_search_index().save_objects(all_tweets_indices)

        elapsed_time = time.time() - start_time
        print(f"Retrieved {len(all_tweets)} posts in {elapsed_time:.2f} seconds")
