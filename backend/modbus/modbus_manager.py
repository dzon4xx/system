import logging
import threading
import time
from serial import SerialException

from common.sys_types import mt, et, task_stat

from common.elements.element import Element, Output_element, Input_element

from common.modules.module import Module, Input_module, Output_module, Anfa_output, Anfa_led_light, Anfa_ambient, Anfa_input

from common.benchmark import Benchmark

from backend.modbus.modbus import Modbus
from sys_database.database import Database, create_db_object

class Modbus_manager(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=None, target=None, name='MODBUS')
                 
        self._db = create_db_object()
        self.logger = logging.getLogger('MODBUS_MAN')

        self.modbus = Modbus(250000)

        self.tasks = None # tasks are instantated by start script

        self._setup()

    def _setup(self, ):
        
        self._db.load_objects_from_table(Anfa_output)
        self._db.load_objects_from_table(Anfa_led_light)
        self._db.load_objects_from_table(Anfa_ambient)
        self._db.load_objects_from_table(Anfa_input)

        for module in Module.items.values():
            module.modbus = self.modbus #pass modbus reference to every module

        for element in Element.items.values():
            module = Module.items[element.module_id]
            module.elements[element.reg_id] = element # pass elements to modules registers

    def _check_tasks(self, ):

        not_done_tasks = set()
        while self.tasks:
            output_module = self.tasks.pop() # get output element form task queue
            output_module.write()

        #    if output_module.is_available():
        #        result = output_module.write()
        #        if result == False:
        #            output_module.timeout = 3
        #            not_done_tasks.add(output_module) # put module to task queue
        #    else:
        #        not_done_tasks.add(output_module)
        #while not_done_tasks:
        #    self.tasks.add(not_done_tasks.pop())

    def run(self, ):
        if (self.modbus.connected):
            time.sleep(1.5) # sleep to allow slaves to configure themselfs
            self.logger.info('Thread {} start'. format(self.name))
            bench = Benchmark()
            while True:
                for input_module in Input_module.items.values(): # loop for every input module to get high response speed
                    self._check_tasks() #after every read of in_mod check if there is anything to write to out_mod
                    if input_module.is_available():
                        input_module.read() # reds values and sets them to elements
                        pass
                for input_element in Input_element.items.values():
                    if input_element.prev_value != input_element.value:
                        input_element.new_val_flag = True
                        self.logger.debug('New val: {}'.format(str(input_element)))
                        input_element.prev_value = input_element.value

                lps = bench.loops_per_second()

        else:
            self.logger.error('Modbus connection error. Thread {} exits'.format(self.name))

