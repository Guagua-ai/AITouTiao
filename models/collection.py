from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, desc
from sqlalchemy.orm import relationship
from models import db
from models.collection_tweet import CollectionsTweets


class Collection(db.Model):
    __tablename__ = 'collections'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)
    tweets = relationship(
        'Tweet', secondary='collections_tweets', back_populates='collections')

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

    def create_collection(user_id, name):
        collection = Collection(name=name, user_id=user_id)
        db.session.add(collection)
        db.session.commit()
        return collection

    def get_collection_by_id(id):
        # update last_accessed_at
        collection = Collection.query.filter_by(id=id).first()
        collection.last_accessed_at = datetime.utcnow()
        db.session.commit()
        return collection

    def get_collections_by_user_id(user_id):
        return Collection.query.filter_by(user_id=user_id).order_by(desc(Collection.last_accessed_at)).all()

    def get_collection_by_id_and_user_id(id, user_id):
        # update last_accessed_at
        collection = Collection.query.filter_by(id=id, user_id=user_id).first()
        collection.last_accessed_at = datetime.utcnow()
        db.session.commit()
        return collection

    def get_tweets(self):
        return self.tweets.filter(CollectionsTweets.collection_id == self.id).all()

    def add_tweet(self, tweet):
        if tweet in self.tweets:
            raise ValueError('Tweet is already in collection')
        # update last_accessed_at
        self.last_accessed_at = datetime.utcnow()
        self.tweets.append(tweet)
        db.session.commit()

    def remove_tweet(self, tweet):
        if tweet not in self.tweets:
            raise ValueError('Tweet is not in collection')
        # update last_accessed_at
        self.last_accessed_at = datetime.utcnow()
        self.tweets.remove(tweet)
        db.session.commit()
