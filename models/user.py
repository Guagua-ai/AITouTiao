from datetime import datetime
from flask_login import UserMixin
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Column, Integer, String, DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


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

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_user_by_id(self, id):
        return User.query.filter_by(id=id).first()
    
    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()
    
    def get_user_by_name(self, name):
        return User.query.filter_by(name=name).first()
    
    def get_all_users(self):
        return User.query.all()
    
    def create_user(self, name, email, password):
        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return user
    
    def update_user(self, id, name, email, password):
        user = User.query.filter_by(id=id).first()
        user.name = name
        user.email = email
        user.password = password
        db.session.commit()
        return user
    
    def delete_user(self, id):
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return user

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User