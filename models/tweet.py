from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from app import db


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
    content = Column(String)

    # Alternatively, you can use this approach for multiple constraints
    __table_args__ = (UniqueConstraint('url'),)

    def __repr__(self):
        return f"<Tweet(id={self.id}, author={self.author}, title={self.title}, url={self.url})>"


class TweetSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Tweet
