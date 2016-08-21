from backend.components.base_component import BaseComponent
from backend.misc.sys_types import Et


class Element(BaseComponent):

    table_name = "elements"
    COL_MODULE_ID, COL_REG,  = 3, 4,
    column_headers_and_types = BaseComponent.column_headers_and_types + [['module_id', 'integer'], ['register', 'integer']]

    items = {}

    def __init__(self, *args):
        super().__init__(args[0], Et(args[1]), args[2])  # inicjalizuj id type, name
        Element.items[self.id] = self        
        self.value = None
        self.module_id = args[Element.COL_MODULE_ID]
        self.reg_id = args[Element.COL_REG]
        self.objects_to_notify = set()
        self.new_val_flag = False

    def subscribe(self, who):
        self.objects_to_notify.add(who)

    def notify_objects(self, ):
        for _object in self.objects_to_notify:
            _object.notify(self.value)

    def __str__(self, ):
        return "".join([super().__str__(), "\tvalue: ", str(self.value)])


class InputElement(Element):

    types = {Et.ds, Et.dht_hum, Et.dht_temp, Et.pir, Et.rs, Et.ls, Et.switch}
    items = {}

    def __init__(self, *args):
        """arguments: type name """
        super().__init__(*args)  # inicjalizuj type, name
        InputElement.items[self.id] = self


class OutputElement(Element):
 
    types = {Et.led, Et.heater, Et.ventilator, Et.blind}

    defualt_priority = 15
    items = {}

    def __init__(self, *args):
        super().__init__(*args)
        OutputElement.items[self.id] = self
        self.desired_value = 0
        self.setter_priority = OutputElement.defualt_priority  # Default priority can be overriden by everybody

    def set_desired_value(self, value, priority, set_flag=False):

        if priority <= self.setter_priority:
            self.desired_value = value

            if set_flag:
                self.setter_priority = priority
            else: 
                self.setter_priority = self.defualt_priority

            return True

        else:
            return False

    def __str__(self, ):
        return "".join([super().__str__(), "\tdesired_value: ", str(self.desired_value)])

    @staticmethod
    def str():
        string = "\n"
        for element in OutputElement.items.values():
            el_str = str(element) 
            string += el_str + "\n"

        return string


class Blind(OutputElement):
    table_name = "blinds"
    column_headers_and_types = Element.column_headers_and_types + [['direction', 'text'], ['other_blind', 'integer']] 

    COL_DIRECTION, COL_OTHER_BLIND = 5, 6
    items = {}

    def __init__(self, *args):
        super().__init__(*args[0:self.COL_DIRECTION])
        Blind.items[self.id] = self
        self.direction = args[self.COL_DIRECTION]
        self.other_blind = args[self.COL_OTHER_BLIND]  # if blind is up then it is down and the other way around
    
    def set_desired_value(self, value, priority, set_flag=False):

        if super().set_desired_value(value, priority, set_flag=False):
            self.other_blind.desired_value = 0
















































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
