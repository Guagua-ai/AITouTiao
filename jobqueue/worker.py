import os
from redis import Redis

conn = Redis.from_url(os.getenv('REDIS_URL'))
