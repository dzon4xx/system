import logging
import time
from time import clock as t

class Benchmark():

    def __init__(self):

        self.prev_counter = 0
        self.counter = 0
        self.snipet_timer = 0   
        self.lps_timer = t() # loops per second timer
        self.lt_timer  = t()      # loop time timer

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
            lps = (self.counter-self.prev_counter)
            self.prev_counter = self.counter
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
