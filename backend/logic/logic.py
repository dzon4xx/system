import logging
import threading
import time

from common.elements.element import Element
from common.elements.input_element import Input_element
from common.elements.output_element import Output_element
from common.elements.clock import clock

from common.relations.dependancy import Dependancy
from common.relations.regulation import Regulation

from sys_database.database import Database, create_db_object

from common.sys_types import mt, et, regt, task_stat

from backend.logic.task import Task


class Logic_manager(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=None, target=None, name='LOGIC')
                 
        self.__comunication = args[0]
        self.__db = create_db_object()
        self.logger = logging.getLogger('LOGIC')

        self.tasks = []

        self.__setup()

    def __setup(self, ):
        self.__db.load_objects_from_table(Input_element)
        self.__db.load_objects_from_table(Output_element)
        self.__db.load_objects_from_table(Dependancy)
        self.__db.load_objects_from_table(Regulation)
   
    def __process_msg(self, msg):
        msg = msg.split(',')
        type = msg[0][0]
        id = int(msg[0][1:])
        val = int(msg[1])
        return type, id, val

    def __check_com_buffer(self, ):
        """Sprawdz bufor komunikacyjny jesli pelny to ustaw desired value"""
        if self.__comunication.out_buffer:
            for msg in self.__comunication.out_buffer:
                type, id, value = self.__process_msg(msg)
                if type == 'e':
                    Output_element.items[id].set_desired_value(0, value) # priorytet wiadomosci od klienta jest najwyzszy - 0. 
                    #self.logger.debug('Set desired value el: %s val: %s', id, value)
                elif type == 'r':
                    Regulation.items[id].set_point = value
            self.logger.debug(Output_element.elements_str())

            #tutaj zalozyc locka zeby komunikacja nie pisala
            self.__comunication.out_buffer = set() # wyczysc bufor

    def __check_elements_values_and_notify(self, ):
        """Sprawdza czy modbus ustawil stany elementow"""
        clock.evaluate_time()
        for element in Element.items.values():
            if element.new_val_flag:
                element.notify_objects() # powiadamia zainteresowane obiekty
                element.new_val_flag = False
                if element.type in (et.pir, et.rs, et.switch, et.heater):
                    msg = 'e' + str(element.id) + ',' + str(element.value) + ',' + 's'
                else:
                    msg = 'e' + str(element.id) + ',' + str(element.value) 
                self.__comunication.in_buffer.add(msg)

    def __evaluate_relations_and_set_des_values(self, ):
        """Sprawdza zaleznosci i regulacje. jesli sa spelnione to wysyla sterowanie"""

        for dep in Dependancy.items.values():
            dep.evaluate_cause()    #sprawdz przyczyne
            for effect in dep.effects: #wykonaj nie wykonane zadania
                if not effect.done:
                    effect.run() #jesli efekt ma wystapic w danym momencie to powiadomi element wyjsciowy

        for reg in Regulation.items.values():
            reg.run()

    def __generate_new_tasks(self,):
        for out_element in Output_element.items.values():
            if out_element.value != out_element.desired_value:
                task = Task(status = task_stat.new,
                            out_element = out_element,
                            value = out_element.desired_value)
                self.tasks.append(task)

    def __clean_done_tasks(self, ):
        self.tasks = [task for task in self.tasks if task.status != task_stat.done]

    def run(self, ):
        self.logger.info('Thread {} start'. format(self.name))
        while True:
            time.sleep(0.1)
            self.__clean_done_tasks()
            self.__check_com_buffer()
            self.__check_elements_values_and_notify()
            self.__evaluate_relations_and_set_des_values()
            self.__generate_new_tasks()



