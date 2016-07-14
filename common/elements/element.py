from common.base_object import Base_object
from common.sys_types import et

class Element(Base_object):

    table_name = "elements"
    column_headers_and_types = Base_object.column_headers_and_types
    ID = 0
    items = {}

    def __init__(self, *args):
        super().__init__(args[0], et(args[1]), args[2]) # inicjalizuj id type, name
        Element.items[self.id] = self        
        self.value = None
        self.module_id = None
        self.objects_to_notify = []   
        self.new_val_flag = False

    def subscribe(self, who):
        self.objects_to_notify.append(who)

    def notify_objects(self, ):
        for object in self.objects_to_notify:
            object.notify(self.value)

    def __str__(self, ):
        return  "".join( [super().__str__(), "\tvalue: ", str(self.value)])

if __name__ == "__main__":
    from common.sys_types import et
    for i in range(4):
        el = Element(et.ds, 'element')
        print (str(el))


















































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
