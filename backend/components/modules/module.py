from backend.components.base_component import Base_component
from backend.misc.sys_types import mt, et
from time import time 

from functools import wraps


def command(func):
    """Decorator for all modbus commands. It counts correct and corupted transmisions. 
        It sets timeout if the transmission was corrupted """
    @wraps(func)
    def func_wrapper(self, *args, **kwargs):
        self.transmission_num += 1 #
        result = func(self)

        if result:    # if there is response from module
            self.correct_trans_num += 1
            return result
        else:
            self.available = False
            self.courupted_trans_num += 1
            if self.timeout <= self.max_timeout:
                self.timeout *= 2 # Increade timeout
            #TODO notification about module failures
            return result
    return func_wrapper

def write_command(func):
    """Decorator for modbus write commands it checks which elements values differ.
        If the communication result is True it updates elements values """
    @wraps(func)
    def func_wrapper(self, *args, **kwargs):
        elements_to_update = []
        for element in self.elements.values():
            if element.desired_value != element.value:   # element value needs to be updated               
                self.values[element.reg_id] = element.desired_value
                elements_to_update.append(element)

        result = func(self)

        if result:
            for element in elements_to_update:
                if element.desired_value != element.value:   # element value needs to be updated
                    element.value = element.desired_value   # element value is updated
                    element.new_val_flag = True

        return result
    return func_wrapper

class Add_element_error(Exception):
    def __init__(self, msg):
        self.msg = msg

class Module(Base_component):
    table_name = 'modules'
    """System modules class"""

    types = set((mt.led_light, mt.output, mt.ambient, mt.input)) #  Needed for loading objects from database
    ID = 0
    start_timeout = 0.01

    items = {}
    def __init__(self, *args):
        super().__init__(args[0], mt(args[1]), args[2])
        Module.items[self.id] = self 
        self.ports = {} # Module's physical ports. Dictionary stores elements during configuration so not to connect elment twice to same port
        self.elements = {}# Module's elements. Keys are registers in which elements values are going to be stored
        self.modbus = None# Reference to modbus. Passed by modbus manager.

        self.available = True# Flag indicating if there is communication with module
        self.last_timeout = 0
        self.timeout = Module.start_timeout
        self.max_timeout = 2 
        self.correct_trans_num = 0
        self.transmission_num = 0
        self.courupted_trans_num = 0

    def is_available(self, ):
        """Checks if module is available. If it is not but timeout expired it makes module available so there would be communication trial"""
        if self.available:
            self.timeout = Module.start_timeout
            return True

        else:
            if time() - self.last_timeout > self.timeout:
                self.last_timeout = time()
                self.available = True
                return True
            
        return False
       
    def check_port_range(self, port):
        if port>self.num_of_ports-1 or port<0:
            raise Add_element_error('Port: ' + str(port) + ' out of range')

    def check_port_usage(self, port):
        try:
            self.ports[port]
            raise Add_element_error('Port: ' + str(port) + ' is in use')
        except KeyError:
            pass

    def check_element_type(self, element):
        if element.type not in self.accepted_elements:
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
        element.reg_id = port
        element.module_id = self.id
        self.elements[element.id] = element

class Input_module(Module):

    types = set((mt.ambient, mt.input))
    items = {}
    def __init__(self, *args):
        super().__init__(*args)
        Input_module.items[self.id] =  self

    @command
    def read(self,):
        regs_values = self.modbus.read_regs(self.id, 0, self.num_of_regs)
        
        if regs_values:
            for element in self.elements.values():
                new_value = regs_values[element.reg_id]
                if new_value != element.value:
                    element.value = new_value
                    element.new_val_flag = True       
            return True

        return False

class Output_module(Module):

    types = set((mt.led_light, mt.output))
    items = {}
    def __init__(self, *args):
        super().__init__(*args)
        Output_module.items[self.id] =  self
        self.values =  [ 0 for i in range(self.num_of_regs) ] # values to be written in board modbus registers

class Output_board(Output_module):


    num_of_ports = 10
    num_of_regs = 10
    accepted_elements = set((et.led, et.heater, et.ventilator, et.blind))
    
    types = set((mt.output,))
    items = {}
    def __init__(self, *args):
        super().__init__(*args)
        Output_board.items[self.id] = self 

    @command
    @write_command
    def write(self, ):
        return self.modbus.write_coils(self.id, 0, self.values)

class Led_light_board(Output_module):
    
    num_of_ports = 3
    num_of_regs = 3
    accepted_elements = set((et.led,))

    types = set((mt.led_light,))
    items = {}
    def __init__(self, *args):
        super().__init__(args[0], mt(args[1]), args[2])
        Led_light_board.items[self.id] = self 

    @command
    @write_command
    def write(self, ):
        return self.modbus.write_regs(self.id, 0, self.values)

class Ambient_board(Input_module):
    

    num_of_ports = 4
    num_of_regs = 19
    accepted_elements = set((et.ds, et.dht_hum, et.dht_temp, et.ls,))

    types = set((mt.ambient,))
    items = {}
    def __init__(self, *args):
        Input_module.__init__(self, *args)
        Ambient_board.items[self.id] =  self
        self.ds18b20_counter = 0
    
    def add_element(self, port, element):
        """For anfa ambient ports are not the same as registers. ds18b20 sensors are all working on one port"""
        self.check_element_type(element)
        self.check_port_range(port)
        self.check_if_element_connected(element)
        try:
            if self.ports[port]:    #Check if something is already on the port
                if self.ports[port].type == et.ds:  # If on this port is ds18b20 
                    if element.type == et.ds:   # And user wants to connect another ds18b20
                        pass # everything is fine
                    else:
                        raise Add_element_error('Port: ' + port + ' in use') # raise error
        except KeyError:           
            self.ports[port] = element # Add element to port

        if element.type == et.ls: # dodanie elementu do rejestru
            element.reg_id = 0
        elif element.type == et.dht_temp:
            element.reg_id = 1
        elif element.type == et.dht_hum:
            element.reg_id = 2
        elif element.type == et.ds:
            element.reg_id = 3 + self.ds18b20_counter
            self.ds18b20_counter += 1
       
        element.module_id = self.id
        self.elements[element.id] = element

class Input_board(Input_module):

    num_of_ports = 15
    num_of_regs = 15
    accepted_elements = set((et.pir, et.rs, et.switch,))

    types = set((mt.input,))
    items = {}
    def __init__(self, *args):
        Input_module.__init__(self, *args)
        Input_board.items[self.id] = self

        


