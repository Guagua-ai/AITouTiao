from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, desc
from sqlalchemy.orm import relationship
from models import db


class Collection(db.Model):
    __tablename__ = 'collections'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)
    tweets = relationship(
        'Tweet', secondary='collections_tweets', lazy='dynamic', back_populates='collections')

    def __repr__(self):
        return f'<Collection {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'last_accessed_at': self.last_accessed_at,
        }
    
    def to_ext_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'userId': self.user_id,
        }

    def create_collection(user_id, name):
        collection = Collection(name=name, user_id=user_id)
        db.session.add(collection)
        db.session.commit()
        return collection

    def get_collection_by_id(id):
        # update last_accessed_at
        collection = Collection.query.filter_by(id=id).first()
        if collection is None:
            return None
        collection.last_accessed_at = datetime.utcnow()
        db.session.commit()
        return collection
    
    def get_collection_by_name(user_id, name):
        # update last_accessed_at
        collection = Collection.query.filter_by(user_id=user_id, name=name).first()
        if collection is None:
            return None
        collection.last_accessed_at = datetime.utcnow()
        db.session.commit()
        return collection

    def get_collections_by_user_id(user_id):
        return Collection.query.filter_by(user_id=user_id).order_by(desc(Collection.last_accessed_at)).all()

    def get_collection_by_id_and_user_id(id, user_id):
        # update last_accessed_at
        collection = Collection.query.filter_by(id=id, user_id=user_id).first()
        if collection is None:
            return None
        collection.last_accessed_at = datetime.utcnow()
        db.session.commit()
        return collection

    def add_tweet_to_collection(self, tweet_id):
        from models.tweet import Tweet
        tweet = Tweet.get_tweet_by_id(tweet_id)
        if tweet is None:
            return None
        self.tweets.append(tweet)
        db.session.commit()
        return tweet

    def get_tweets(self):
        from models.tweet import Tweet
        return Tweet.query.filter(Tweet.collections.contains(self)).all()
