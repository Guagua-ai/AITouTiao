import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_connection():
    engine = create_engine(os.getenv('DATABASE_URL') + '/news_dev')
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
