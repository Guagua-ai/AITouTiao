# worker.py
import os
from redis import Redis
from rq import Worker, Queue, Connection
from dotenv import load_dotenv
from db import db
from models.user import User

# Load environment variables
load_dotenv('.env')
listen = ['default']
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
conn = Redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        print(worker.work())
