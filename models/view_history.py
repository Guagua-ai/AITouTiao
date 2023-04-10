import datetime
from sqlalchemy import Column, Integer, String, DateTime
from models import db


class ViewHistory(db.Model):
    __tablename__ = 'view_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    post_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Add a unique constraint on the (user_id, post_id) pair
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', 'timestamp'),
    )

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
        return view_history

    def get_view_history_by_user_id(user_id):
        return ViewHistory.query.filter_by(user_id=user_id).order_by(ViewHistory.timestamp.desc()).all()

    def get_view_history_by_post_id(post_id):
        return ViewHistory.query.filter_by(post_id=post_id).all()

    def get_view_history_by_user_id_and_post_id(user_id, post_id):
        return ViewHistory.query.filter_by(user_id=user_id, post_id=post_id).first()

    def get_view_history_by_user_id_and_post_id(user_id, post_id):
        return ViewHistory.query.filter_by(user_id=user_id, post_id=post_id).first()

    def get_view_history_by_user_id_and_post_id(user_id, post_id):
        return ViewHistory.query.filter_by(user_id=user_id, post_id=post_id).first()

    def get_view_history_by_user_id_and_post_id(user_id, post_id):
        return ViewHistory.query.filter_by(user_id=user_id, post_id=post_id).first()

    def get_view_history_by_user_id_and_post_id(user_id, post_id):
        return ViewHistory.query.filter_by(user_id=user_id, post_id=post_id).first()
