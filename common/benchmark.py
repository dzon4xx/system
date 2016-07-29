import logging
import time
from time import clock as t

class Benchmark():

    def __init__(self):
        self.logger = logging.getLogger('BENCHMARK')
        self.counter = 0
        self.snipet_timer = 0   
        self.lps_timer = t() # loops per second timer
        self.lt_timer  = t()      # loop time timer
        self.min_lt = 10000
        self.max_lt = -1
        self.min_loops_ps = 10000000
        self.max_loops_ps = 0

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
        lt = self.loop_time()
        if lt < self.min_lt:
             self.min_lt = lt
        if lt > self.max_lt:
            self.max_lt = lt
            print (self.max_lt)
        if t() - self.lps_timer >= 1:
            self.lps_timer = t()
            lps = (self.counter)
            self.counter = 0
            #self.logger.info('Loops per second: {}\n Min loop time {} Max predicted loops: {}\n Max loop time {} Min predicted loops: {}'.format(lps, self.min_lt, int(1/self.min_lt),self.max_lt, int(1/self.max_lt)))
            return lps


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
