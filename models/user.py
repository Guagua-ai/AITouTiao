from datetime import datetime
from flask_login import UserMixin
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Column, Integer, String, DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager
from db import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False, default='user')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
    quota = Column(Integer, default=40)
    profile_image = Column(
        String(200), default='https://source.boringavatars.com/beam/30/name')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def is_admin(self):
        return self.role == 'admin'

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_user_by_id(id):
        return User.query.filter_by(id=id).first()

    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    def get_user_by_name(name):
        return User.query.filter_by(name=name).first()

    def get_all_users():
        return User.query.all()

    def create_user(name, email, password, role='user', quota=100, profile_image=None):
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            quota=quota)
        if profile_image:
            user.profile_image = profile_image
        db.session.add(user)
        db.session.commit()
        return user

    def update_user(id, name=None, email=None, password=None, profile_image=None, role=None, quota=None):
        assert id, 'No id provided'
        user = User.query.filter_by(id=id).first()

        assert name or email or password or profile_image or role or quota, 'No data to update'
        if name:
            user.name = name
        if email:
            user.email = email
        if password:
            user.password = password
        if profile_image:
            user.profile_image = profile_image
        if role:
            user.role = role
        if quota:
            user.quota = quota
        db.session.commit()
        return user

    def delete_user(id):
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return user


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
