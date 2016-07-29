from common.base_object import Base_object
from common.sys_types import et
from math import floor

class Element(Base_object):

    table_name = "elements"
    COL_MODULE_ID, COL_REG,  = 3, 4, #numery kolumn
    column_headers_and_types = Base_object.column_headers_and_types + [['module_id', 'integer'], ['register', 'integer']] 

    items = {}
    def __init__(self, *args):
        super().__init__(args[0], et(args[1]), args[2]) # inicjalizuj id type, name
        Element.items[self.id] = self        
        self.value = None
        self.module_id = args[Element.COL_MODULE_ID]
        self.reg_id = args[Element.COL_REG]
        self.objects_to_notify = []   
        self.new_val_flag = False

    def subscribe(self, who):
        self.objects_to_notify.append(who)

    def notify_objects(self, ):
        for object in self.objects_to_notify:
            object.notify(self.value)

    def __str__(self, ):
        return  "".join( [super().__str__(), "\tvalue: ", str(self.value)])

class Input_element(Element):

    types = set((et.ds, et.dht_hum, et.dht_temp, et.pir, et.rs, et.ls, et.switch))
    items = {}

    def __init__(self, *args):
        """arguments: type name """
        super().__init__(*args) # inicjalizuj type, name
        Input_element.items[self.id] = self     
        self.prev_value = None
        self.unit = None  

    def __str__(self, ):
        return  "".join([super().__str__(), "\tprev val: ", str(self.prev_value), ])

class Output_element(Element):
 
    types = set((et.led, et.heater, et.ventilator, et.blind))

    defualt_priority = 10
    items = {}
    def __init__(self, *args):
        super().__init__(*args)
        Output_element.items[self.id] = self 
        self.desired_value = None
        self.setter_priority = Output_element.defualt_priority   #bardzo niski priorytet. kazy moze go zmienic

    def set_desired_value(self, priority, val):
        if val > 0:
            if priority <= self.setter_priority:
                self.setter_priority = priority
                self.desired_value = val
                return True
        elif val == 0:# przy wylaczeniu kazdy moze ustawic element
            self.setter_priority = Output_element.defualt_priority
            self.desired_value = 0 
            return False


    def __str__(self, ):
        return  "".join([super().__str__(), "\tdesired_value: ", str(self.desired_value)])#str(self.desired_value), "\tmodule id: ", str(self.module_id), "\tport id: ", str(self.reg_id)])

    def elements_str():
        string = "\n"
        for element in Output_element.items.values():
            el_str = str(element) 
            string += el_str + "\n"

        return string

class Blind(Output_element):
    table_name = "blinds"
    column_headers_and_types = Element.column_headers_and_types + [['direction', 'text'], ['other_blind', 'integer']] 

    COL_DIRECTION, COL_OTHER_BLIND = 5, 6
    items = {}
    def __init__(self, *args):
        super().__init__(*args[0:self.COL_DIRECTION])
        Blind.items[self.id] = self
        self.direction = args[self.COL_DIRECTION]
        self.other_blind = args[self.COL_OTHER_BLIND] # if blind is up then it is down and the other way around

    def set_desired_value(self, priority, val):
        if super(Blind, self).set_desired_value(priority, 1): # if setter has right priority to turn on blind
            self.other_blind.desired_value = 0    # other blind motor is turned off as well ot avoid shortcut
            return True
        return False


if __name__ == "__main__":
    pass

from common.sys_types import et
types = set((et.ds, et.dht_hum, et.dht_temp, et.pir, et.rs, et.ls, et.switch))
num_types = set()

while types:
    num_types.add(types.pop().value)

num_types



















































#kontaktron, pir
#class Input(Element):
#    def __init__(self, name):      
#        return super().__init__(name)


#class Digital_input(Input):
#        def __init__(self, name):
#            return super().__init__(name)

#class Analog_input(Input):
#    def __init__(self, name):
#        return super().__init__(name)

#class Output(Element):
#    def __init__(self, name):       
#        return super().__init__(name)

#class Analog_output(Output):
#    def __init__(self, name):
#        return super().__init__(name)

#class Digital_output(Output):
#    def __init__(self, name):
#        return super().__init__(name)

#class PIR(Digital_input):
#    def __init__(self, name):
#                return super().__init__(name)

#class Reed_switch(Digital_input):
#    def __init__(self, name):
#                return super().__init__(name)


#class DS18B20(Analog_input):
#    def __init__(self, name):
#        return super().__init__(name)


#class DHT22(Analog_input):
#    def __init__(self, name):
#        return super().__init__(name)

#class Light_sensor(Analog_input):
#    def __init__(self, name):
#        return super().__init__(name)


#class Heater(Digital_output):
#    def __init__(self, name):
#        return super().__init__(name)

#class Blind():
#    def __init__(self, name):
#        pass

#class Led(Analog_output):
#    def __init__(self, name):
#        pass
