import redis
from datetime import datetime as dt
import time

r = redis.Redis( host="127.0.0.1", port=6379 )

class RateLimitExceeded (Exception):
    def __init__(self, message="RateLimitExceeded: Wait for 10 seconds"):
        super().__init__(self,message)

def rate_limit(func):
    def inner(param, *args, **kwargs):
        
        ## LIMIT PARAMETERS
        # Allow 20 requests in 10 second window
        RATE_LIMIT = 20
        RATE_LIMIT_SEC = 5

        ## Getting Existing value in Rate Bucket ( identified by the ##param value )
        x = r.get(param)         
        make_req = False

        ## If no such bucket exist, allow request and make bucket with TTL
        if (x == None):
            r.setex(param, RATE_LIMIT_SEC, RATE_LIMIT - 1)
            make_req = True
    
        ## If Bucket value is zero or less, deny request
        elif int(x) <= 0:
            make_req = False

        ## Other wise allow request, and decrement bucket value
        else:
            r.decrby(param, 1)
            make_req = True
        
        ## Check for request allowed and accordingly make request or raise Rate Limit Exceeded 
        if make_req:
            func(param, *args, **kwargs)
        else:
            raise RateLimitExceeded()
    
    return inner

## RATE LIMIT the function using python decorators
@rate_limit
def printer(param):
    print(f"[ {dt.utcnow().strftime('%Y-%m-%d %H:%M:%S.%fZ')} ] {__file__}: Hello World - {param}")

if __name__ == '__main__':
    ## Wait time in seconds
    exponent_wait_duration = 1
    for i in range(1000):
        try: 
            printer("Tester")
            exponent_wait_duration = 1
        except RateLimitExceeded:
            ## Mitigating Rate Limit with Exponential Backoff
            print(f"Rate Limit Exceeded: Exponential Backoff with wait of {exponent_wait_duration} seconds ")
            time.sleep(exponent_wait_duration)
            exponent_wait_duration = exponent_wait_duration * 2