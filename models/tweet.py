import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, desc
from sqlalchemy.orm import relationship
from models.view_history import ViewHistory
from models.collection import Collection
from models.collection_tweet import CollectionsTweets
from models.like import Like
from models import db


class Tweet(db.Model):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    source_id = Column(String)
    source_name = Column(String)
    author = Column(String)
    display_name = Column(String)
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
    likes = relationship('User', secondary='likes', lazy='subquery',
                         backref=db.backref('liked_tweets', lazy=True))
    num_likes = Column(Integer, default=0)

    # Alternatively, you can use this approach for multiple constraints
    __table_args__ = (UniqueConstraint('url'),)

    def __repr__(self):
        return f"<Tweet(id={self.id}, author={self.author}, displayname={self.display_name}, title={self.title}, url={self.url})>"

    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'source_name': self.source_name,
            'author': self.author,
            'display_name': self.display_name,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'url_to_image': self.url_to_image,
            'published_at': self.published_at,
            'created_at': self.created_at,
            'content': self.content,
            'num_likes': self.num_likes
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

    def add_tweet(source_id, source_name, author, display_name, title, description, url, url_to_image, published_at, content):
        new_tweet = Tweet(source_id=source_id, 
                          source_name=source_name, 
                          author=author, 
                          display_name=display_name,
                          title=title,
                          description=description, 
                          url=url, 
                          url_to_image=url_to_image, 
                          published_at=published_at, 
                          created_at=datetime.now(),
                          content=content)
        db.session.add(new_tweet)
        db.session.commit()

    def update_tweet(id, source_id=None, source_name=None, author=None, display_name=None, title=None, description=None, url=None, url_to_image=None, published_at=None, content=None):
        tweet_to_update = Tweet.query.filter_by(id=id).first()
        if source_id is not None:
            tweet_to_update.source_id = source_id
        if source_name is not None:
            tweet_to_update.source_name = source_name
        if author is not None:
            tweet_to_update.author = author
        if display_name is not None:
            tweet_to_update.display_name = display_name
        if title is not None:
            tweet_to_update.title = title
        if description is not None:
            tweet_to_update.description = description
        if url is not None:
            tweet_to_update.url = url
        if url_to_image is not None:
            tweet_to_update.url_to_image = url_to_image
        if published_at is not None:
            tweet_to_update.published_at = published_at
        if content is not None:
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
    
    def like(self):
        self.num_likes += 1
        db.session.commit()

    def unlike(self):
        if self.num_likes > 0:
            self.num_likes -= 1
        db.session.commit()


class TweetSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Tweet
