from common.base_object import Base_object
from enum import Enum
from common.sys_types import mt, et


class Add_element_error(Exception):
    def __init__(self, msg):
        self.msg = msg

class Module(Base_object):
    """System modules class"""

    accepted_elements = {mt.input : [et.pir, et.rs],
                        mt.output: [et.heater, et.led, et.ventilator, et.led, et.blind],
                        mt.ambient: [et.ds, et.ls, et.dht_hum, et.dht_temp],
                        mt.led_light: [et.led]}

    input_modules = [mt.input, mt.ambient]

    output_modules = [mt.led_light, mt.output]
  
    ports_map = {mt.input: 15,
                 mt.ambient: 4,
                 mt.led_light: 3,
                 mt.output : 10}

    ID = 0
    items = {}

    def __init__(self, *args):
        super().__init__(*args)
        Module.items[self.id] = self 
        self.num_of_ports = Module.ports_map[self.type]
        self.ports = self.__create_ports()

    def __create_ports(self, ):
        return [None for port_num in range(self.num_of_ports)]

    def check_port_range(self, port):
        if port>self.num_of_ports-1 or port<0:
            raise Add_element_error('Port: ' + str(port) + ' out of range')

    def check_port_usage(self, port):
        if self.ports[port] != None:
            raise Add_element_error('Port: ' + str(port) + ' is in use')

    def check_element_type(self, element):
        if element.type not in Module.accepted_elements[self.type]:
            raise Add_element_error('Element: ' + element.type.name + ' is not valid for ' +self.type.name)
        
    def check_if_element_connected(self, element):
        if element.module_id != None and element.module_id != self.id and element.type != et.blind: # roleta moze byc podlaczona 2 razy do jednego modulu - gora i dol
            raise Add_element_error('Element: ' + str(element.id) + ' already connected to ' + str(element.module_id))

    def add_element(self, port, element):
        self.check_element_type(element)
        self.check_port_range(port)
        self.check_port_usage(port)
        self.check_if_element_connected(element)

        self.ports[port] = element
        if element.type != et.blind:
            element.module_id = self.id

    def __str__(self, ):
        return "".join([super().__str__(), '\tFree ports:\t', ",".join([str(port_num) for port_num, port in enumerate(self.ports) if port==None])])



    #def __str__(self):
    #    return "".join([super().__str__(), '\nREGS:\n', "\n".join([str(element) for element in self.regs])])








