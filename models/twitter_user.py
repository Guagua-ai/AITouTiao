from sqlalchemy import Column, Integer, String
from models import db
from models.like import Like


class TwitterUser(db.Model):
    __tablename__ = 'twitter_users'

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    username = Column(String)
    display_name = Column(String)
    profile_image_url = Column(String)

    def __repr__(self):
        return f"<TwitterUser(id={self.id}, user_id={self.user_id}, username={self.username}, display_name={self.display_name}, profile_image_url={self.profile_image_url})>"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'display_name': self.display_name,
            'profile_image_url': self.profile_image_url,
        }

    def check_if_needs_update(self):
        return self.display_name == None or self.profile_image_url == None

    def create_user(user_id, username, display_name=None, profile_image_url=None):
        user = TwitterUser(user_id=user_id, 
                           username=username,
                           display_name=display_name, 
                           profile_image_url=profile_image_url)
        db.session.add(user)
        db.session.commit()
        return user

    def update(username, display_name, profile_image_url):
        user = TwitterUser.query.filter_by(username=username).first()
        user.display_name = display_name
        user.profile_image_url = profile_image_url
        db.session.commit()
        return user

    def get_user_by_id(user_id):
        return TwitterUser.query.filter_by(user_id=user_id).first()

    def get_user_by_user_id(user_id):
        return TwitterUser.query.filter_by(user_id=user_id).first()

    def get_user_by_username(username):
        return TwitterUser.query.filter_by(username=username).first()

    def get_user_by_display_name(display_name):
        return TwitterUser.query.filter_by(display_name=display_name).first()

    def get_all_users():
        return TwitterUser.query.all()
