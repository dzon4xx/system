from backend.components.base_component import Base_component
from backend.misc.sys_types import et
from math import floor

class Element(Base_component):

    table_name = "elements"
    COL_MODULE_ID, COL_REG,  = 3, 4, #numery kolumn
    column_headers_and_types = Base_component.column_headers_and_types + [['module_id', 'integer'], ['register', 'integer']] 

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
         
class Output_element(Element):
 
    types = set((et.led, et.heater, et.ventilator, et.blind))

    defualt_priority = 15
    items = {}
    def __init__(self, *args):
        super().__init__(*args)
        Output_element.items[self.id] = self 
        self._desired_value = 0
        self.setter_priority = Output_element.defualt_priority   #bardzo niski priorytet. kazy moze go zmienic

        self.is_desired_value_set = False

    @property
    def desired_value(self,):
        return self._desired_value

    @desired_value.setter
    def desired_value(self, args):
        value = args[0]
        priority = args[1]
        set_flag = args[2]

        if priority <= self.setter_priority:
            self._desired_value = value            
            self.is_desired_value_set = True

            if set_flag:
                self.setter_priority = priority
            else: 
                self.setter_priority = Output_element.defualt_priority          

        else:
            self.is_desired_value_set = False

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
    
    @Output_element.desired_value.setter
    def desired_value(self, args):
        super(Blind, self.__class__).desired_value.fset(self, args)
        if self.is_desired_value_set:
            self.other_blind._desired_value = 0


if __name__ == "__main__":
    pass

from backend.misc.sys_types import et
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
