import logging
import threading
import time
import queue

from backend.components.elements.element import Element
from backend.components.elements.element import Input_element, Output_element, Blind
from backend.components.modules.module import Output_module

from backend.components.elements.clock import clock

from backend.components.relations.dependancy import Dependancy
from backend.components.relations.regulation import Regulation

from backend.misc.sys_types import mt, et, regt, task_stat


class Logic_manager(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=None, target=None, name='LOGIC')
                 
        self._comunication_out_buffer = args[0]
        self._comunication_in_buffer = args[1]
        self._application_priority = 5
        self.logger = logging.getLogger('LOGIC')
        self.tasks = queue.Queue()

        self.__setup()

    def __setup(self, ):

        for blind in Blind.items.values():
            other_blind_id  =   blind.other_blind
            blind.other_blind = Blind.items[other_blind_id]
  
    def __process_msg(self, msg):
        msg = msg.split(',')
        type = msg[0][0]
        id = int(msg[0][1:])
        val = int(msg[1])
        return type, id, val

    def __check_com_buffer(self, ):
        """Sprawdz bufor komunikacyjny jesli pelny to ustaw desired value"""
        while not self._comunication_out_buffer.empty():
            msg = self._comunication_out_buffer.get()             
            type, id, value = self.__process_msg(msg)
            if type == 'e':
                set_flag = False
                if value > 0:
                    set_flag = True
                Output_element.items[id].desired_value = (value, self._application_priority, set_flag) # priorytet wiadomosci od klienta jest najwyzszy - 0. 
                self.logger.debug('Set desired value el: %s val: %s', id, value)
            elif type == 'r':
                Regulation.items[id].set_point = value
                self._comunication_in_buffer.put(msg)
            self.logger.debug(Output_element.elements_str())

    def __check_elements_values_and_notify(self, ):
        """Sprawdza czy modbus ustawil stany elementow"""
        clock.evaluate_time()
        for element in Element.items.values():
            if element.new_val_flag:
                self.logger.info(element) 
                element.new_val_flag = False
                element.notify_objects() # powiadamia zainteresowane obiekty
                if element.type in (et.pir, et.rs, et.switch, et.heater, et.blind):
                    msg = 'e' + str(element.id) + ',' + str(element.value) + ',' + 's'
                else:
                    msg = 'e' + str(element.id) + ',' + str(element.value)                   
                self._comunication_in_buffer.put(msg)

    def __evaluate_relations(self, ):
        """Sprawdza zaleznosci i regulacje. jesli sa spelnione to wysyla sterowanie"""

        for dep in Dependancy.items.values():
            dep.evaluate_cause()    #sprawdz przyczyne
            for effect in dep.effects: #wykonaj nie wykonane zadania
                if not effect.done:
                    effect.run() #jesli efekt ma wystapic w danym momencie to powiadomi element wyjsciowy

        for reg in Regulation.items.values():
            reg.run()

    def __generate_new_tasks(self,):
        """Generates queue with modules which have elements with changed value"""
        modules_to_notify = set()
        for out_element in Output_element.items.values():
            if out_element.value != out_element.desired_value:
                modules_to_notify.add(Output_module.items[out_element.module_id])

        while modules_to_notify:
            self.tasks.put(modules_to_notify.pop())

    def run(self, ):
        self.logger.info('Thread {} start'. format(self.name))
        while True:            
            time.sleep(0.1)
            self.__check_com_buffer()
            self.__check_elements_values_and_notify()
            self.__evaluate_relations()
            self.__generate_new_tasks()


if __name__ == "__main__":
    from backend.objects_loader import objects_loader
    objects_loader()
    com_out_buffer = queue.Queue()
    com_in_buffer = queue.Queue()
    logic = Logic_manager(args=(com_out_buffer, com_in_buffer,))
    logic.logger.disabled = False
    logic.logger.setLevel("DEBUG")

    Dependancy.items[1].conditions[0].notify(0)

    while True:
        logic.run()

