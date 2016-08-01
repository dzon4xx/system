import operator
import time

from backend.components.elements.element import Element, Input_element, Output_element
from backend.components.elements.clock import clock

from backend.misc.sys_types import effect_status

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
        self._op = Condition.operator_dict[op]
        self.comp_val = comp_val
        self._val = None

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value

    def evaluate(self):
        out_val = self._op(self._val, self.comp_val)
        return ' ' + str(out_val) + ' '

    def notify(self, val):
        self._val = val

    def __str__(self, ):
        """Representation of object"""
        return "".join(["ID: ",str(self.id),"\teval: ", self.evaluate()])

class Effect():

    def __init__(self, id, el_id, value, time):
        self.id = id
        self.el_id = el_id
        self.value = value
        self.prev_value = None
        self.time = self.__parse_time(time)
        self.priority = 5

        self.done = True # Should the effect be started. if not done it should be started
        self.set_flag = False # Does the effect should set its value. If false it sets prev value
        self.cause_time = None # Time of cause triger

    def __parse_time(self, time):
        if time == '':
            return 0
        else:
            return int(time)

    def notify(self, milis):
        self.cause_time = milis
        self.done = False

    def run(self, ):
        if self.set_flag:   
            if get_millis()-self.cause_time >= self.time:
                output_element = Output_element.items[self.el_id]
                self.prev_value = output_element.value
                status = output_element.desired_value = (self.value, self.priority, True)
                self.done = True
                return True
            return False
        else:
            status = Output_element.items[self.el_id].desired_value = (self.prev_value, self.priority, False)
            self.done = True

    def __repr__(self,):
        return "El id: {} done: {}".format(self.el_id, self.done)

class Dependancy():

    table_name = 'dependancy'

    items = {}
    column_headers_and_types = [['id', 'integer primary key'], 
                                ['name', 'text'],
                                ['dep_str', 'text']]

    cond_start = '[' #marker poczatku warunku
    cond_stop = ']'
    effect_start_t = '{' #marker poczatku czasu efektu
    effect_stop_t = '}'
    cond_marker = '!' # marker przeczyny wstawiany w stringa przyczyn. Potem w to miejsce wstawiana jest wartosc wyrazenia przyczyny (True, False)
    cause_effect_sep = 'then' #separator pomiedzy przyczynami a efektami
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
        self.effects = []     #efekty, ktore wydarza sie po spelnieniu przyczyny

        self.num_of_conds = 0
        self.num_of_effect = 0
        self.num_of_done_effect = 0

        self.prev_cause_result = False

        cause_str, effect_str = dep_str.split(Dependancy.cause_effect_sep)
        self.cause_template = "" # szablon przyczyny do ktorego wstrzykiwane sa wartosci warunkow.
        self.__parse_cause(cause_str)
        self.__parse_effect(effect_str)
       
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

        pass

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

    def __parse_effect(self, effect_str):
        effect_str = effect_str.strip().rstrip(';')
        effect_array = effect_str.split(';')
        for effect in effect_array:
            effect = effect.strip()
            op_pos = 0
            time_pos = None
            time = ''
            is_time = False
            for s_pos, s in enumerate(effect):
                if s == '=':
                    op_pos = s_pos
                   
                if s == Dependancy.effect_start_t:
                    time_pos = s_pos
                    is_time = True 

                if is_time:
                    time += s

                if s == Dependancy.effect_stop_t:
                    is_time = False 

            element_id = int(effect[1:op_pos])

            if element_id not in Output_element.items.keys():
                raise Dependancy_config_error('Output element: ' + str(element_id) + ' not in output elements')
            
            time = time[1:-1] # pierwszy i ostatni znak to markery poczatku i konca czasu
            set_value = int(effect[op_pos+1:time_pos])
            
            effect = Effect(self.num_of_effect, element_id, set_value, time)
            self.num_of_effect += 1
            self.effects.append(effect)
        
    def evaluate_cause(self, ):
        eval_causes = ''
        condition_num = 0
        for s in self.cause_template:
            if s == Dependancy.cond_marker:
                eval_causes += self.conditions[condition_num].evaluate()
            else:
                eval_causes += s
       
        cause_result = eval(eval_causes)
        
        if cause_result and not self.prev_cause_result: # if the cause changes from False to True
            for effect in self.effects:
                effect.cause_time = get_millis() # notyfikacja tylko gdy przyczyna zmieni sie z false na true
                effect.done = False
                effect.set_flag = True

        if not cause_result and self.prev_cause_result: # if the cause changes from True to False effects should be undone
            for effect in self.effects:
                effect.done = False
                effect.set_flag = False

        self.prev_cause_result = cause_result

        return cause_result

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

