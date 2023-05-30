from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.tweet import Tweet
from models import db


class Headliner(db.Model):
    __tablename__ = 'headliners'

    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, db.ForeignKey('tweets.id'), nullable=False)
    title = Column(String)
    image_url = Column(String)
    published_at = Column(DateTime)
    created_at = Column(DateTime)

    tweet_id = Column(Integer, ForeignKey('tweets.id'), nullable=True)

    def __repr__(self):
        return f"<Headliner(id={self.id}, tweet_id={self.tweet_id}, image_url={self.image_url})>"

    def to_dict(self):
        return {
            'id': self.id,
            'tweet_id': self.tweet_id,
            'title': self.title,
            'image_url': self.image_url,
        }

    def add_headliner(tweet_id, title, image_url):
        headliner = Headliner(
            tweet_id=tweet_id,
            title=title,
            image_url=image_url,
        )
        db.session.add(headliner)
        db.session.commit()
        return headliner

    def delete_headliner(headliner_id):
        headliner = Headliner.query.get(headliner_id)
        db.session.delete(headliner)
        db.session.commit()
        return headliner_id

    def update_headliner(headliner_id, title, image_url):
        headliner = Headliner.query.get(headliner_id)
        headliner.title = title
        headliner.image_url = image_url
        db.session.commit()
        return headliner

    def get_headliner(headliner_id):
        headliner = Headliner.query.get(headliner_id)
        return headliner

    def get_headliners():
        headliners = Headliner.query.all()
        return headliners

    def get_headliners_by_tweet_id(tweet_id):
        headliners = Headliner.query.filter_by(tweet_id=tweet_id).all()
        return headliners
