import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_connection():
    engine = create_engine(os.getenv('DATABASE_URL') + '/news_dev')
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
