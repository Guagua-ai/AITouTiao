from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models import db


class Like(db.Model):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    tweet_id = Column(Integer, ForeignKey('tweets.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="likes")
    tweet = relationship("Tweet", back_populates="likes")

    def __repr__(self):
        return '<Like {}>'.format(self.id)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tweet_id': self.tweet_id,
            'created_at': self.created_at,
        }

    def create_like(user_id, tweet_id):
        like = Like(user_id=user_id, tweet_id=tweet_id)
        db.session.add(like)
        db.session.commit()
        return like

    def get_like_by_id(id):
        return Like.query.filter_by(id=id).first()

    def get_like_by_user_id_and_tweet_id(user_id, tweet_id):
        return Like.query.filter_by(user_id=user_id, tweet_id=tweet_id).first()

    def get_likes_by_user_id(user_id):
        return Like.query.filter_by(user_id=user_id).all()

    def get_likes_by_tweet_id(tweet_id):
        return Like.query.filter_by(tweet_id=tweet_id).all()
    
    def get_likes_by_user_id_and_tweet_ids(user_id, tweet_ids):
        return Like.query.filter(Like.user_id == user_id, Like.tweet_id.in_(tweet_ids)).all()

    def unlike_by_id(id):
        like = Like.get_like_by_id(id)
        db.session.delete(like)
        db.session.commit()
        return like

    def unlike_by_user_id_and_tweet_id(user_id, tweet_id):
        like = Like.get_like_by_user_id_and_tweet_id(user_id, tweet_id)
        db.session.delete(like)
        db.session.commit()
        return like
