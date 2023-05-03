import time

class RateLimiter:
    def __init__(self, requests_per_minute_limit, tokens_per_minute_limit):
        self.last_request_time = None
        self.requests_per_minute_limit = requests_per_minute_limit
        self.tokens_per_minute_limit = tokens_per_minute_limit
        self.tokens_used_in_last_minute = 0

    def rate_limit(self, tokens):
        if self.last_request_time is not None:
            time_since_last_request = time.time() - self.last_request_time
            if time_since_last_request < 60 / self.requests_per_minute_limit:
                time.sleep((60 / self.requests_per_minute_limit) - time_since_last_request)

            if time_since_last_request >= 60:
                self.tokens_used_in_last_minute = 0

        self.tokens_used_in_last_minute += tokens
        if self.tokens_used_in_last_minute > self.tokens_per_minute_limit:
            time_to_wait = 60 - time_since_last_request
            if time_to_wait > 0:
                time.sleep(time_to_wait)

        self.last_request_time = time.time()
