import operator
import time

from common.elements.element import Element
from common.elements.clock import clock
from common.elements.input_element import Input_element
from common.elements.output_element import Output_element

from common.sys_types import efect_status

get_millis = lambda: int(round(time.time() * 1000))

class Dependancy_config_error(Exception):
    def __init__(self, msg):
        self.msg = msg

class Condition():

    operator_dict = {'=': operator.eq,
                     '<': operator.lt,
                     '>': operator.gt,
                     '|': operator.contains}

    def __init__(self, id,  op, comp_val):
        self.id = id
        self.__op = Condition.operator_dict[op]
        self.comp_val = comp_val
        self.val = None

    def evaluate(self):
        out_val = self.__op(self.val, self.comp_val)
        return ' ' + str(out_val) + ' '


    def notify(self, val):
        self.val = val

    def __str__(self, ):
        """Representation of object"""
        return "".join(["ID: ",str(self.id),"\teval: ", self.evaluate()])

class Efect():

    def __init__(self, id, el_id, value, time):
        self.id = id
        self.el_id = el_id
        self.value = value
        self.time = self.__parse_time(time)
        self.priority = 1

        self.done = False # flaga mowiaca o tym czy wystartowac dany efekt. Zmieniana na True po kazdym pozytywnym wyliczeniu przyczyny. Jesli efekt wykonany to przechodzi do stanu False
        self.cause_time = None # Moment uruchomienia przyczyny

    def __parse_time(self, time):
        if time == '':
            return 0
        else:
            return int(time)

    def notify(self, milis):
        self.cause_time = milis
        self.done = False

    def run(self, ):
        if get_millis()-self.cause_time>self.time:
            Output_element.items[self.el_id].set_desired_value(self.priority, self.value)
            self.done = True
            return True
        return False


class Dependancy():

    table_name = 'dependancy'

    items = {}
    column_headers_and_types = [['id', 'integer primary key'], 
                                ['name', 'text'],
                                ['dep_str', 'text']]

    cond_start = '[' #marker poczatku warunku
    cond_stop = ']'
    efect_start_t = '{'
    efect_stop_t = '}'
    cond_marker = '!' # marker przeczyny wstawiany w stringa przyczyn. Potem w to miejsce wstawiana jest wartosc wyrazenia przyczyny (True, False)
    cause_efect_sep = 'then' #separator pomiedzy przyczynami a efektami
    time_marker = 't'
    day_marker = 'd'
    element_marker = 'e'

    day_dict = {'mon': 0,
            'tue': 1,
            'wed': 2,
            'thu': 3,
            'fri': 4,
            'sat': 5,
            'sun': 6,}


    def __init__(self, id, name, dep_str):
        self.id =  id
        Dependancy.items[self.id] =  self

        self.name = name
        self.dep_str = dep_str
        self.conditions = [] #lista warunkow aby przyczyna zaleznosci byla spelniona
        self.efects = []     #efekty, ktore wydarza sie po spelnieniu przyczyny

        self.num_of_conds = 0
        self.num_of_efects = 0
        self.num_of_done_efects = 0


        cause_str, efect_str = dep_str.split(Dependancy.cause_efect_sep)
        self.cause_template = "" # szablon przyczyny do ktorego wstrzykiwane sa wartosci warunkow.
        self.__parse_cause(cause_str)
        self.__parse_efects(efect_str)
       
    def __parse_cause(self, cause_str):
        condition_num = 0
        condition = ''
        condition_pos = None
        is_condition = False
        self.cause_template = ''
         
        for s_pos, s in enumerate(cause_str):

            if s == Dependancy.cond_start:
                is_condition = True
                condition_pos = s_pos
                self.cause_template += Dependancy.cond_marker
            
            if is_condition:
                condition += s
            else:
                self.cause_template += s

            if s == Dependancy.cond_stop:
                is_condition = False
                condition = condition[1:-1] #ostatni i pierwszy znak to markery poczatku i konca warunku
                self.__parse_condition(condition)               
                condition = ''
                confition_pos = None

    def __parse_condition(self, condition):
        """Parsuje string warunku i tworzy obiekt warunku czasowego lub zwyklego"""

        op_pos = 0
        op = None   #operator
        for s_pos, s in enumerate(condition):
            if s in Condition.operator_dict.keys():
                op_pos = s_pos
                op = s
                break

        element = condition[:op_pos]
        comp_value = condition[op_pos+1:]
        if element[0] == Dependancy.element_marker:
            element_id = int(element[1:])

            if element_id not in Input_element.items.keys():
                raise Dependancy_config_error('Input element: ' + str(element_id) + ' not in input elements')
            comp_value = int(comp_value)
            subscribe = Element.items[element_id].subscribe
            

        if element[0] == Dependancy.day_marker:
            comp_value = comp_value.split(',')
            comp_value = [Dependancy.day_dict[day] for day in comp_value]
            subscribe = clock.subscribe_for_day_notification

        if element[0] == Dependancy.time_marker:
            comp_value = comp_value.split(':')
            comp_value = [int(val) for val in comp_value]
            subscribe = clock.subscribe_for_minute_notification

        condition = Condition(self.num_of_conds, op, comp_value)
        self.num_of_conds += 1
        subscribe(condition)
        self.conditions.append(condition)

    def __parse_efects(self, efect_str):
        efect_str = efect_str.strip().rstrip(';')
        efects = efect_str.split(';')
        for efect in efects:
            efect = efect.strip()
            op_pos = 0
            time_pos = None
            time = ''
            is_time = False
            for s_pos, s in enumerate(efect):
                if s == '=':
                    op_pos = s_pos
                   
                if s == Dependancy.efect_start_t:
                    time_pos = s_pos
                    is_time = True 

                if is_time:
                    time += s

                if s == Dependancy.efect_stop_t:
                    is_time = False 

            element_id = int(efect[1:op_pos])

            if element_id not in Output_element.items.keys():
                raise Dependancy_config_error('Output element: ' + str(element_id) + ' not in output elements')
            
            time = time[1:-1] # pierwszy i ostatni znak to markery poczatku i konca czasu
            set_value = int(efect[op_pos+1:time_pos])
            
            efect = Efect(self.num_of_efects, element_id, set_value, time)
            self.num_of_efects += 1
            self.efects.append(efect)
        
    def evaluate_cause(self, ):
        eval_causes = ''
        condition_num = 0
        for s in self.cause_template:
            if s == Dependancy.cond_marker:
                eval_causes += self.conditions[condition_num].evaluate()
            else:
                eval_causes += s

        self.evaluate_cause.prev_result = False
        result = eval(eval_causes)

        if result and  not self.evaluate_cause.prev_result:
            self.evaluate_cause.prev_result = result
            for efect in efects:
                efect.notify(get_millis())

        return result



    def __str__(self, ):    
        return "".join(["ID: ",str(self.id),"\ttype: ", "\tname: ", self.name, '\tdep_str: ', self.dep_str])

if __name__ == "__main__":
    dep1 = '[d=mon,tue,wed,thu,fri] and [t=5:50] then e3=20{0}; e3=0{200}; e4=1{0}'
    dep2 = '([d=mon,tue,wed] and [t=6:50]) or e8>15 then e3=20; e2=1; e4=7'
    dep3 = '[d=mon,thu,fri] and [t=8:50] then e3=20'



    d1 = Dependancy(1, '', dep1)
    d2 = Dependancy(2, '', dep2)
    d3 = Dependancy(3, '', dep3)

    print (d1.evaluate_cause())

