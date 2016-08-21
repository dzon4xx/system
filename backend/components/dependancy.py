import operator

from backend.components.clock import Clock
from backend.components.element import Element, OutputElement


class DependancyConfigError(Exception):
    def __init__(self, msg):
        self.msg = msg


class Condition:
    """Condition is a part of a cause.
    Condition is true when it's value  compared to compare_value returns True
    given one of "=", "<", ">", "|" operators"""
    operator_dict = {'=': operator.eq,
                     '<': operator.lt,
                     '>': operator.gt,
                     '|': operator.contains}

    def __init__(self, _id,  op, comp_val):
        self.id = _id
        self._op = Condition.operator_dict[op]
        self.comp_val = comp_val
        self.val = None

    def evaluate(self):
        try:
            out_val = self._op(self.val, self.comp_val)
            return ' ' + str(out_val) + ' '  # Value is returned as a string because it goes to eval()
        except TypeError:
            return ' ' + str(False) + ' '

    def notify(self, val):
        self.val = val

    def __repr__(self, ):
        return "".join(["ID: ", str(self.id), "comp_val: ", self.comp_val, "op: ", self._op])

    def __str__(self, ):
        """Representation of object"""
        return "".join(["ID: ", str(self.id), "\teval: ", self.evaluate()])


class Effect:

    clock = Clock()

    def __init__(self, _id, out_el, value, _time):
        self.id = _id
        self.output_element = out_el
        self.value = value
        self.prev_value = None
        self.time = _time
        self.priority = 5

        self.done = True  # Should the effect be started. if not done it should be started
        self.cause_time = None  # Time when cause was True

    def start(self, milis):
        """Api for notifing effect that couse changed to True and at what time"""
        self.cause_time = milis
        self.done = False
        self.prev_value = self.output_element.value

    def run(self, ):
        """Sets desired value of element if it was not set yet and if the time is right"""
        if not self.done:
            if self.clock.get_millis()-self.cause_time >= self.time:
                self.done = self.output_element.set_desired_value(self.value, self.priority, set_flag=True)
                return True
        return False

    def revert(self):
        """Reverts effect. Sets output_element previous value"""
        if self.done:  # efect can be reverted only once when it is done
            self.output_element.desired_value = self.prev_value

    def __repr__(self,):
        return "El id: {} done: {}".format(self.el_id, self.done)


class Dependancy:

    table_name = 'dependancy'

    column_headers_and_types = [['id', 'integer primary key'], 
                                ['name', 'text'],
                                ['dep_str', 'text']]

    cond_start = '['  # flag of condition start
    cond_stop = ']'
    effect_start_t = '{'  # flag of effect start
    effect_stop_t = '}'
    cond_marker = '!'  # flag used by cause parser to mark conditions places.
    cause_effect_sep = 'then'  # separates cause and effects
    time_marker = 't'
    day_marker = 'd'
    element_marker = 'e'

    day_dict = {'mon': 0,
                'tue': 1,
                'wed': 2,
                'thu': 3,
                'fri': 4,
                'sat': 5,
                'sun': 6, }
    clock = Clock()
    items = {}

    def __init__(self, _id, name, dep_str):
        self.id = _id
        Dependancy.items[self.id] = self

        self.name = name
        self.dep_str = dep_str
        self.conditions = []  # Conditions which make the cause
        self.effects = []     # Effects which will happen after condition changes from False to True

        self.num_of_conds = 0
        self.num_of_effect = 0

        self.prev_cause_result = False

        self.cause_str, self.effects_str = dep_str.split(Dependancy.cause_effect_sep)
        self.cause_template = ''  # evaluated conditions are applied to it. Finnally template goes to eval()
               
    def run(self, ):
        """Evaluates cause. If it is true and prev result is false it notifies all efects.
       When the cause changes from True to false it restores effects to initial state """
      
        cause_result = self._evaluate_cause()
        
        if cause_result and not self.prev_cause_result:  # if the cause changes from False to True
            for effect in self.effects:
                effect.start(self.clock.get_millis())

        # if the cause changes from True to False effects should be undone
        if not cause_result and self.prev_cause_result:
            for effect in self.effects:
                effect.revert()

        self.prev_cause_result = cause_result

        for effect in self.effects:
            effect.run()  # perform effect

    def _evaluate_cause(self):
        eval_cause_string = ''
        condition_num = 0
        for s in self.cause_template:  # Evaluate all conditions and put their results into eval strin
            if s == Dependancy.cond_marker:
                eval_cause_string += self.conditions[condition_num].evaluate()
                condition_num += 1
            else:
                eval_cause_string += s

        return eval(eval_cause_string)

    def _parse_cause(self, all_elements=dict()):
        """Parses cause string"""

        for condition in self._find_condition():

            element, op, comp_value = self._parse_condition(condition)

            if element[0] == Dependancy.element_marker:
                element_id = int(element[1:])

                if element_id not in all_elements:
                    raise DependancyConfigError('Element does not exists: ' + str(element_id))
                comp_value = int(comp_value)
                subscribe = all_elements[element_id].subscribe

            if element[0] == Dependancy.day_marker:
                comp_value = comp_value.split(',')
                comp_value = [Dependancy.day_dict[day] for day in comp_value]
                subscribe = self.clock.subscribe_for_weekday

            if element[0] == Dependancy.time_marker:
                comp_value = comp_value.split(':')
                comp_value = [int(val) for val in comp_value]
                subscribe = self.clock.subscribe_for_minute

            condition = Condition(self.num_of_conds, op, comp_value)
            self.num_of_conds += 1
            subscribe(condition)
            self.conditions.append(condition)

    def _find_condition(self):
        """Yields condition and updates cause template"""
        condition = ''

        is_condition = False
        for s_pos, s in enumerate(self.cause_str):

            if s == Dependancy.cond_start:
                is_condition = True
                self.cause_template += Dependancy.cond_marker

            if is_condition:
                condition += s
            else:
                self.cause_template += s

            if s == Dependancy.cond_stop:
                yield condition[1:-1]  # First and last char are flags of begining and end of condition
                is_condition = False
                condition = ''

    @staticmethod
    def _parse_condition(condition):
        """Creates condition objects based on condition string"""

        op_pos = 0
        op = None  # operator
        for s_pos, s in enumerate(condition):
            if s in Condition.operator_dict.keys():
                op_pos = s_pos
                op = s
                break

        element = condition[:op_pos]
        comp_value = condition[op_pos+1:]

        if op not in Condition.operator_dict.keys():
            raise DependancyConfigError("Condition has wrong operator: {}".format(op))

        return element, op, comp_value

    def _parse_effects(self, output_elements=None):
        """Creates effect objects based on effect string"""

        effects_array = self.effects_str.strip().rstrip(';').split(';')
        for effect_str in effects_array:

            element_id, set_value, _time = self._parse_effect(effect_str)

            if element_id not in output_elements.keys():
                raise DependancyConfigError('Output element: ' + str(element_id) + ' not in output elements')

            effect = Effect(self.num_of_effect, output_elements[element_id], set_value, _time)
            self.num_of_effect += 1
            self.effects.append(effect)

    @staticmethod
    def _parse_effect(effect_str):

        effect_str = effect_str.strip()
        op_pos = 0
        time_pos = None
        _time = ''
        is_time = False
        for s_pos, s in enumerate(effect_str):
            if s == '=':
                op_pos = s_pos

            if s == Dependancy.effect_start_t:
                time_pos = s_pos
                is_time = True

            if is_time:
                _time += s

            if s == Dependancy.effect_stop_t:
                is_time = False

        try:
            element_id = int(effect_str[1:op_pos])
            set_value = int(effect_str[op_pos + 1:time_pos])
            _time = int(effect_str[time_pos+1:-1])*1000  # First and last char are flags of begining and end of time
        except:
            raise DependancyConfigError('Effect parsing error. Effect string: {}'.format(effect_str))

        if set_value < 0:
            raise DependancyConfigError('Set value cant be negative. Effect string: {}'.format(effect_str))

        if _time < 0:
            raise DependancyConfigError('Time cant be negative. Effect string: {}'.format(effect_str))

        return element_id, set_value, _time

    def __str__(self, ):    
        return "".join(["ID: ", str(self.id), "\ttype: ", "\tname: ", self.name, '\tdep_str: ', self.dep_str])

    def __repr__(self):
        return "".join(["ID: ", str(self.id), " - ", self.name])


