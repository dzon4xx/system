import logging
import threading
import time

from backend.components.elements.element import Element, Input_element 
from backend.components.modules.module import Module, Input_module
from backend.misc.benchmark import Benchmark
from backend.modbus.modbus import Modbus

class Modbus_manager(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=None, target=None, name='MODBUS')
                 
        self.logger = logging.getLogger('MODBUS_MAN')
 
        self.modbus = Modbus(38400)
        self.tasks = args[0]

        self._setup()

    def _setup(self, ):
        
        for module in Module.items.values():
            module.modbus = self.modbus #pass modbus reference to every module

        for element in Element.items.values():
            module = Module.items[element.module_id]
            module.elements[element.reg_id] = element # pass elements to modules registers

    def _check_tasks(self, ):

        while not self.tasks.empty():
            
            output_module = self.tasks.get() # get output element form task queue
            if output_module.is_available():
                result = output_module.write()
                if result == False:
                    output_module.available = False 


    def run(self, ):
        if (self.modbus.connected):
            time.sleep(0.5) # sleep to allow slaves to configure themselfs
            self.logger.info('Thread {} start'. format(self.name))
            
            bench = Benchmark(self.logger.level)
            bench.start()
            while True:
                for input_module in Input_module.items.values(): # loop for every input module to get high response speed
                    self._check_tasks() #after every read of in_mod check if there is anything to write to out_mod
                    if input_module.is_available():
                            input_module.read() # reds values and sets them to elements

                if self.modbus.consecutive_corrupted_frames > 1:
                    self.modbus.serial.close()
                    self.modbus.open_serial()
                    self.modbus.consecutive_corrupted_frames = 0
                    self.logger.error("Serial reload")
                        
                #is_second_passed = bench.loops_per_second()
                #if is_second_passed:
                #    self.modbus.debug()

        else:
            self.logger.error('Modbus connection error. Thread {} exits'.format(self.name))

if __name__ == "__main__":
    import queue
    from timeit import default_timer as t
    from backend.misc.color_logs import color_logs

    from backend.objects_loader import objects_loader

    start = t()
    color_logs()
    objects_loader()
    tasks = queue.Queue()
    modbus_manager = Modbus_manager(args=(tasks,))
    modbus_manager.logger.disabled = False
    modbus_manager.logger.setLevel("DEBUG")
    
    print("Set up took: {0:.2f} miliseconds".format((t()-start)*1000))
    while True:
        modbus_manager.run()

