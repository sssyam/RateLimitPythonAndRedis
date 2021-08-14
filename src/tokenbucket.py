import datetime
import time

class RateLimitExceeded(Exception):
    def __init__(self, msg=""):
        super().__init__(msg)

class Limiter:
    def __init__(self, burst, refill, time, debug = False):
        self.bucket = burst
        self.burst_limit = burst                            ## Bucket Max Capacity
        self.refill_value = refill                          ## Bucket Refill Value
        self.duration = time * 10**6                        ## duration b/w fills in u_second
        self.timestamp = int(datetime.datetime.utcnow().timestamp() * 10**6)  ## Current timestamp in u_second
        self._debug = debug

    def fill(self):
        ## get current time in MicroSeconds
        now = int(datetime.datetime.utcnow().timestamp() * 10**6)
        
        ## Check how much time has elapsed
        delta = now - self.timestamp

        ## If elapsed time delta is greater than duration
        if delta >= self.duration:
            # if self._debug:
            #     print("Refilling Bucket: " + str(delta))

            ## FILL Bucket
            self.bucket = min(self.burst_limit, self.bucket + int(delta/self.duration) * self.refill_value )

            ## Set expiry timestamp to now + delta duration
            self.timestamp = int(now)

    def use(self):
        self.bucket = self.bucket - 1
    
    def debug(self):
        print("Bucket: " + str(self.bucket), end="|")
        print("Expiry: " + str(self.timestamp), end="|")
        now = int(datetime.datetime.utcnow().timestamp()* 10**6)
        delta = now - self.timestamp
        print("Now: " + str(now), end="|")
        print("Delta: " + str(delta))

    def request(self, caller):
        # if self._debug:
        #     self.debug()

        ## Fill Before any operation
        self.fill()
        
        # if self._debug:
        #     self.debug()

        ## If bucket token is not zero
        if self.bucket > 0:
            caller()
            self.use()
        else:  ## Or raise a RateLimitExceeded error
            raise RateLimitExceeded("Please Retry")

    
def do_something():
    print("Made request")

if __name__ == "__main__":
    limiter = Limiter(10, 5, 1) ## L10_5
    exponential = 1
    
    while True:
        try:
            limiter.request(do_something)
            exponential = 1
        except RateLimitExceeded as r:
            print("RateLimitExceeded: Sleeping for {} seconds".format(exponential))
            time.sleep(exponential)
            exponential = 2 * exponential