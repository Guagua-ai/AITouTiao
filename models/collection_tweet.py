from sqlalchemy import Column, ForeignKey, Integer
from models import db


class CollectionsTweets(db.Model):
    __tablename__ = 'collections_tweets'

    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey(
        'collections.id'), nullable=False)
    tweet_id = Column(Integer, ForeignKey(
        'tweets.id'), nullable=False)
