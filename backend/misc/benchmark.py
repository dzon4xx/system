import logging
import time
from timeit import default_timer as t

class Benchmark():
    """Calculates number of loops in a second. Useful for testing communication speed"""
    def __init__(self, logging_level):
        self.logger = logging.getLogger('BENCHMARK')
        self.logger.disabled = False
        self.logger.setLevel(logging_level)
        self.counter = 0
        self.snipet_timer = 0   
        self.lps_timer = 0 # loops per second timer
        self.lt_timer  = 0      # loop time timer
        self.min_lt = 10000
        self.max_lt = -1
        self.min_loops_ps = 10000000
        self.max_loops_ps = 0

    def start(self,):
        t()

    def start_timing_snippet(self, ):
        self.snipet_timer = t()

    def get_snippet_time(self, ):
        return t()-self.snipet_timer

    def loop_time(self):
        lt = t() - self.lt_timer
        self.lt_timer = t()
        return lt

    def loops_per_second(self,):
        self.counter += 1
        if t() - self.lps_timer >= 1:
            self.lps_timer = t()
            lps = self.counter
            self.counter = 0
            #print('Loops per second: {} '.format(lps))       
            self.logger.debug('Loops per second: {} '.format(lps))
            return True
        else:
            return False


if __name__ == "__main__":
    bench = Benchmark()
    while True:
        a = 0
        for i in range(100000):
            a+=1
        #print (bench.loop_time())
        lps = bench.loops_per_second()
        if lps:
            print (lps)
from time import clock as t
lt_timer = 0
def loop_time():
    global lt_timer
    lt = t() - lt_timer
    lt_timer = t()
    return lt
