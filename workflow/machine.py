from rq import Queue
from redis import Redis

# Create a subclass of Queue that uses the Redis connection from the environment variable
class FlowMachine(Queue):
    def __init__(self, connection, *args, **kwargs):
        super().__init__(connection=Redis.from_url(connection), *args, **kwargs)