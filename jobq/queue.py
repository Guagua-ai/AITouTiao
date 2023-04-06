import os
from rq import Queue
from redis import Redis

# Create a subclass of Queue that uses the Redis connection from the environment variable
class NewsQueue(Queue):
    def __init__(self, url, *args, **kwargs):
        super().__init__(connection=url, *args, **kwargs)
        self.queue = Queue(connection=self.connection)
