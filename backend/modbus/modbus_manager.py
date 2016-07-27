import logging
import threading
import time
from serial import SerialException

from common.sys_types import mt, et, task_stat
from common.elements.input_element import Input_element
from common.elements.output_element import Output_element
from common.elements.element import Element

from common.modules.input_module import Input_module
from common.modules.output_module import Output_module
from common.modules.module import Module

from common.benchmark import Benchmark

from backend.modbus.modbus import Modbus
from sys_database.database import Database, create_db_object

class Modbus_manager(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=None, target=None, name='MODBUS')
                 
        self._db = create_db_object()
        self.logger = logging.getLogger('MODBUS_MAN')

        self.modbus = Modbus(250000)
        self.modbus.logger.disabled = False
        self.tasks = None # tasks are instantated by start script

        self._setup()

    def _setup(self, ):
        
        self._db.load_objects_from_table(Input_module)
        self._db.load_objects_from_table(Output_module)

        for module in Module.items.values():
            module.modbus = self.modbus #pass modbus reference to every module

        for input_element in Input_element.items.values():
            Input_module.items[input_element.module_id].regs[input_element.reg_id] = input_element

        #for output_element in Output_element.items.values():
        #    Output_module.items[output_element.module_id].regs[input_element.reg_id] = input_element

    def _check_tasks(self, ):

        output_module_to_write = dict() # dictionary for performing modbus write nad notifying output elements
        while not self.tasks.empty():
            output_element = self.tasks.get() # get output element form task queue
            output_module = Output_module.items[output_element.module_id]
            output_module.regs_values[output_element.reg_id]

            if output_module not in output_module_to_write.keys():
                output_module_to_write[output_module] = []
                output_module_to_write[output_module].append(output_element)
            else:
                output_module_to_write[output_module].append(output_element)

        for output_module, output_elements in output_module_to_write.items():
            result = output_module.write()
            if result:
                for output_element in output_elements:
                    output_element.new_val_flag = True
                    output_element.value = output_element.desired_value

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
                    else: 
                        input_module.set_timeout(3) # after [n] seconds try to establish communication with module 
                for input_element in Input_element.items.values():
                    if input_element.prev_value != input_element.value:
                        input_element.new_val_flag = True
                        input_element.prev_value = input_element.value
                        self.logger.debug('New val: {}'.format(str(input_element)))


                lps = bench.loops_per_second()
                if lps:
                    self.logger.debug(lps)
        else:
            self.logger.error('Modbus connection error. Thread {} exits'.format(self.name))

