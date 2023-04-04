from models.user import db as user_db
from models.tweet import db as tweet_db


def setup_db():
    user_db.create_all()
    tweet_db.create_all()
