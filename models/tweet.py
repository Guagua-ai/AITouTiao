import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, desc
from sqlalchemy.orm import relationship
from models.view_history import ViewHistory
from models.collection import Collection
from models.collection_tweet import CollectionsTweets
from models import db


class Tweet(db.Model):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    source_id = Column(String)
    source_name = Column(String)
    author = Column(String)
    title = Column(String)
    description = Column(String)
    # Add the unique constraint directly to the column
    url = Column(String, unique=True)
    url_to_image = Column(String)
    published_at = Column(DateTime)
    created_at = Column(DateTime)
    content = Column(String)

    collections = relationship(
        'Collection', secondary='collections_tweets', back_populates='tweets')

    # Alternatively, you can use this approach for multiple constraints
    __table_args__ = (UniqueConstraint('url'),)

    def __repr__(self):
        return f"<Tweet(id={self.id}, author={self.author}, title={self.title}, url={self.url})>"

    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'source_name': self.source_name,
            'author': self.author,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'url_to_image': self.url_to_image,
            'published_at': self.published_at,
            'created_at': self.created_at,
            'content': self.content,
        }

    def get_all_tweets():
        return Tweet.query.order_by(Tweet.published_at.desc()).all()

    def get_tweets_by_ids(ids):
        return Tweet.query.filter(Tweet.id.in_(ids)).all()

    def get_tweet_by_id(id):
        return Tweet.query.filter_by(id=id).first()

    def get_tweet_by_url(url):
        return Tweet.query.filter_by(url=url).first()

    def get_tweet_by_author(author):
        return Tweet.query.filter_by(author=author).all()

    def get_tweet_by_keywords(keywords):
        return Tweet.filter(
            Tweet.content.ilike(f'%{"%".join(keywords)}%')).order_by(Tweet.published_at.desc()).all()

    def count_tweets():
        return Tweet.query.count()

    def add_tweet(source_id, source_name, author, title, description, url, url_to_image, published_at, content):
        new_tweet = Tweet(source_id=source_id, 
                          source_name=source_name, 
                          author=author, 
                          title=title,
                          description=description, 
                          url=url, 
                          url_to_image=url_to_image, 
                          published_at=published_at, 
                          created_at=datetime.now(),
                          content=content)
        db.session.add(new_tweet)
        db.session.commit()

    def update_tweet(id, source_id, source_name, author, title, description, url, url_to_image, published_at, content):
        tweet_to_update = Tweet.query.filter_by(id=id).first()
        tweet_to_update.source_id = source_id
        tweet_to_update.source_name = source_name
        tweet_to_update.author = author
        tweet_to_update.title = title
        tweet_to_update.description = description
        tweet_to_update.url = url
        tweet_to_update.url_to_image = url_to_image
        tweet_to_update.published_at = published_at
        tweet_to_update.content = content
        db.session.commit()

    def delete_tweet(id):
        tweet_to_delete = Tweet.query.filter_by(id=id).first()
        db.session.delete(tweet_to_delete)
        db.session.commit()

    @staticmethod
    def get_view_history(user_id):
        tweets = Tweet.query.filter(Tweet.id.in_(db.session.query(
            ViewHistory.post_id).filter_by(user_id=user_id))).all()
        return tweets


class TweetSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Tweet
