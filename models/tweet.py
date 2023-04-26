from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from models.view_history import ViewHistory
from models.collection import Collection
from models.collection_tweet import CollectionsTweets
from models.like import Like
from models import db
from utils.time import standard_format

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
    visibility = Column(String, default="private")

    collections = relationship(
        'Collection', secondary='collections_tweets', back_populates='tweets')
    likes = relationship('Like', back_populates='tweet',
                         lazy='subquery', cascade='all, delete-orphan')
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
            'num_likes': self.num_likes,
            'visibility': self.visibility.value,
        }
    
    def to_int_dict(self, needs_content=False):
        return {
            'id': self.id,
            'source': {
                'id': self.source_id,
                'name': self.source_name
            },
            'author': self.author,
            'displayname': self.display_name,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'urlToImage': self.url_to_image,
            'publishedAt': standard_format(self.published_at),
            'createdAt': standard_format(self.created_at),
            'content': self.content if needs_content else '',
            'numLike': self.num_likes,
            'isLiked': False,
            'isCollected': False,
            'visibility': self.visibility,
        }
    
    def to_ext_dict(self, needs_content=False):
        return {
            'id': self.id,
            'source': {
                'id': self.source_id,
                'name': self.source_name
            },
            'author': self.author,
            'displayname': self.display_name,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'urlToImage': self.url_to_image,
            'publishedAt': standard_format(self.published_at),
            'createdAt': standard_format(self.created_at),
            'content': self.content if needs_content else '',
            'numLike': self.num_likes,
            'isLiked': False,
            'isCollected': False,
        }

    def to_index_dict(self):
        return {
            "objectID": self.id,
            "author": self.author,
            "display_name": self.display_name,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "url_to_image": self.url_to_image,
            "published_at": self.published_at,
            "content": self.content,
        }
    
    def approve(self):
        self.visibility = "public"
        db.session.commit()
    
    def flag(self):
        self.visibility = "reviewing"
        db.session.commit()

    def get_all_tweets(visibility="private"):
        if visibility == "reviewing" or visibility == "public":
            return Tweet.query.filter_by(visibility=visibility).order_by(Tweet.published_at.desc()).all()
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

    def add_tweet(source_id, source_name, author, display_name, title, description, url, url_to_image, content, published_at=datetime.now(), visibility='private'):
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
                          content=content,
                          visibility=visibility)
        db.session.add(new_tweet)
        db.session.commit()
        return new_tweet

    def update_tweet(id, source_id=None, source_name=None, author=None, display_name=None, title=None, description=None, url=None, url_to_image=None, published_at=None, content=None, visibility=None):
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
        if visibility is not None:
            tweet_to_update.visibility = visibility
        db.session.commit()
        return tweet_to_update

    def delete(self):
        for collection in self.collections:
            collection.remove_tweet(self)
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_view_history(user_id):
        tweets = Tweet.query.filter(Tweet.id.in_(db.session.query(
            ViewHistory.post_id).filter_by(user_id=user_id))).all()
        return tweets

    def like_count(self):
        if self.num_likes is None:
            self.num_likes = 0
        return self.num_likes

    def add_like(self, like):
        if self.num_likes is None:
            self.num_likes = 0
        self.num_likes += 1
        self.likes.append(like)
        db.session.commit()

    def remove_like(self, like):
        if self.num_likes > 0:
            self.num_likes -= 1
        if like in self.likes:
            self.likes.remove(like)
        db.session.commit()

    def get_likes(self):
        return self.likes
