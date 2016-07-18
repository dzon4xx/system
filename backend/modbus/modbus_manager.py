import threading
import logging

from common.sys_types import mt, et, task_stat
from common.elements.input_element import Input_element
from common.elements.output_element import Output_element
from common.elements.element import Element

from common.modules.input_module import Input_module
from common.modules.output_module import Output_module
from common.modules.module import Module

from backend.modbus.modbus import Modbus
from sys_database.database import Database, create_db_object

class Modbus_manager(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=None, target=None, name='MODBUS')
                 
        self.__db = create_db_object()
        self.logger = logging.getLogger('MODBUS_MAN')
        self.modbus = Modbus('COM7', 1000000)

    def __create_modules(self, ):
        
        self.__db.load_objects_from_table(Input_module)
        self.__db.load_objects_from_table(Output_module)

        for module in Module.items.values():
            module.modbus = self.modbus #pass modbus reference to every module

        for element in Element.items.values():
            Module.items[element.module_id].add_element(element.reg_id, element)

    def __check_tasks(self, ):
        for task in self._tasks:
            if task.status == task_stat.new:
                result = Output_module.items[task.out_element.module_id].write(element.port, element.desired_value)
                if result:
                    task.status = task_stat.done
                    element.value = element.desired_value
                    element.new_val_flag = True

    def run(self, ):
        while True:
            for input_module in Input_module.items.values(): # loop for every input module to get high response speed
                self.__check_tasks() #after every read of in_mod check if there is anything to write to out_mod
                module.read() # reds values and sets them to elements
                for input_element in input_module.elements:
                    if input_element.prev_value != input_element.value:
                        element.new_val_flag = True
                        element.value = value