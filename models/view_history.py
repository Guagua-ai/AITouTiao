import datetime
from sqlalchemy import Column, Integer, String, DateTime
from models import db


class ViewHistory(db.Model):
    __tablename__ = 'view_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False)
    post_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<ViewHistory id={self.id}, user_id={self.user_id}, post_id={self.post_id}, timestamp={self.timestamp}>"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'timestamp': self.timestamp,
        }

    def add_to_view_history(user_id, post_id):
        view_history = ViewHistory(user_id=user_id, post_id=post_id)
        db.session.add(view_history)
        db.session.commit()

    @classmethod
    def get_view_history_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all().order_by(cls.timestamp.desc())

    @classmethod
    def get_view_history_by_post_id(cls, post_id):
        return cls.query.filter_by(post_id=post_id).all()

    @classmethod
    def get_view_history_by_user_id_and_post_id(cls, user_id, post_id):
        return cls.query.filter_by(user_id=user_id, post_id=post_id).first()

    @classmethod
    def get_view_history_by_user_id_and_post_id(cls, user_id, post_id):
        return cls.query.filter_by(user_id=user_id, post_id=post_id).first()

    @classmethod
    def get_view_history_by_user_id_and_post_id(cls, user_id, post_id):
        return cls.query.filter_by(user_id=user_id, post_id=post_id).first()

    @classmethod
    def get_view_history_by_user_id_and_post_id(cls, user_id, post_id):
        return cls.query.filter_by(user_id=user_id, post_id=post_id).first()

    @classmethod
    def get_view_history_by_user_id_and_post_id(cls, user_id, post_id):
        return cls.query.filter_by(user_id=user_id, post_id=post_id).first()
