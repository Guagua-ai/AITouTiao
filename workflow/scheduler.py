from rq_scheduler import Scheduler
from redis import Redis

# Create a subclass of Scheduler that uses the Redis connection from the environment variable
class FlowScheduler(Scheduler):
    def __init__(self, connection, *args, **kwargs):
        super().__init__(connection=Redis.from_url(connection), *args, **kwargs)