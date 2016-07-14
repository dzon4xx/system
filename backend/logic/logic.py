import logging
import threading


from common.elements.element import Element
from common.elements.input_element import Input_element
from common.elements.output_element import Output_element
from common.elements.clock import clock

from common.relations.dependancy import Dependancy
from common.relations.regulation import Regulation

from common.color_logs import color_logs

from sys_database.database import Database, create_db_object

from common.sys_types import mt, et, regt, task_stat

from backend.logic.task import Task
from backend.communication.communication import Communication


class Logic(threading.Thread):

    def __init__(self, comunication):
        super().__init__(self, )
        self.__comunication = comunication
        self.__db = create_db_object()
        self.__logger = logging.getLogger('LOGIC')
        self.tasks = []

        self.__setup()

    def __setup(self, ):
        self.__create_elements()
        self.__create_dependancies()
        self.__create_regulations()

    def __create_elements(self, ):
        input_elements_table = self.__db.get_table(Input_element)
        output_elements_table = self.__db.get_table(Output_element)
        for input_element_data in input_elements_table:
            input_element_data = list(input_element_data)
            input_element_data[Input_element.COL_TYPE] = et(input_element_data[Input_element.COL_TYPE]) # konwersja typu z int do enum
            Input_element(*input_element_data)

        for output_element_data in output_elements_table:
            output_element_data = list(output_element_data)
            output_element_data[Input_element.COL_TYPE] = et(output_element_data[Input_element.COL_TYPE]) # konwersja typu z int do enum
            Output_element(*output_element_data)

    def __create_dependancies(self,):
        dependancies_table = self.__db.get_table(Dependancy)
        for dependancy_data in dependancies_table:
            Dependancy(*dependancy_data)

    def __create_regulations(self,):
        pass

    def __process_msg(self, msg):
        msg = msg.split(',')
        return [int(val) for val in msg]

    def __check_com_buffer(self, ):
        """Sprawdz bufor komunikacyjny jesli pelny to ustaw desired value"""
        if self.__comunication.out_buffer:
            for msg in self.__comunication.out_buffer:
                el_id, value = self.__process_msg(msg)
                Element.items[el_id].set_desired_value(0, value) # priorytet wiadomosci od klienta jest najwyzszy - 0. 
            self.__comunication.out_buffer = [] # wyczysc bufor

    def __check_elements_values_and_notify(self, ):
        """Sprawdza czy modbus ustawil stany elementow"""
        clock.evaluate_time()
        for element in Element.items.values():
            if element.new_val_flag:
                element.notify_objects()
                element.new_val_flag = False
                self.__comunication.in_buffer.append((element.id, element.value))

    def __evaluate_relations_and_set_des_values(self, ):
        """Sprawdza zaleznosci i regulacje. jesli sa spelnione to wysyla sterowanie"""

        for dep in Dependancy.items.values():
            dep.evaluate_cause()
            for effect in dep.effects:
                if not effect.done:
                    effect.run() #jesli efekt ma wystapic w danym momencie to powiadomi element wyjsciowy

    def __generate_tasks(self,):
        for out_element in Output_element.items.values():
            if out_element.value != out_element.desired_value:
                task = Task(status = task_stat.new,
                            out_element = out_element,
                            value = out_element.desired_value)
                self.tasks.append(task)

    def run(self, ):
        self.__check_com_buffer()
        self.__check_elements_values_and_notify()
        self.__evaluate_relations_and_set_des_values()
        self.__generate_tasks()


