from functools import wraps

from backend.components.base_component import BaseComponent
from backend.components.clock import Clock
from backend.components.modbus_network import ModbusNetwork
from backend.misc.sys_types import Mt, Et


class AddElementError(Exception):
    def __init__(self, msg):
        self.msg = msg


class Module(BaseComponent):
    """Base class for all modules.
    It implements prototype of command that decorates all read and write functions"""

    table_name = 'modules'

    types = {Mt.led_light, Mt.output, Mt.ambient, Mt.input}  # Needed for loading objects from database
    ID = 0
    start_timeout = 10  # timeout in ms
    clock = Clock()
    items = {}

    def __init__(self, *args):

        super().__init__(args[0], Mt(args[1]), args[2])
        Module.items[self.id] = self 
        self.ports = {}  # Module's physical ports. Dictionary stores elements during configuration so not to connect elment twice to same port
        self.elements = {}  # Module's elements. Keys are registers in which elements values are going to be stored
        self.modbus = ModbusNetwork()  # Reference to modbus. Modbus is a singleton.

        self.available = True  # Flag indicating if there is communication with module
        self.last_timeout = 0
        self.timeout = Module.start_timeout
        self.max_timeout = 2 
        self.correct_trans_num = 0
        self.transmission_num = 0
        self.courupted_trans_num = 0

    def is_available(self, ):
        """Checks if module is available.
        If it is not but timeout expired it makes module
        available so there would be communication trial"""
        if self.available:
            self.timeout = Module.start_timeout
            return True

        else:
            current_time = self.clock.get_millis()
            if current_time - self.last_timeout >= self.timeout:
                self.last_timeout = current_time
                self.available = True
                return True
        return False

    @staticmethod
    def command(func):
        """Decorator for all modbus commands. It counts correct and corupted transmisions.
            It sets timeout if the transmission was corrupted """

        @wraps(func)
        def func_wrapper(self, ):
            self.transmission_num += 1
            result = func(self)

            if result:  # if there is response from module
                self.correct_trans_num += 1
                return result
            else:
                self.available = False
                self.courupted_trans_num += 1
                if self.timeout <= self.max_timeout:
                    self.timeout *= 2  # Increase timeout
                # TODO notification about module failures
                return result
        return func_wrapper

    def check_port_range(self, port):
        if port > self.num_of_ports-1 or port < 0:
            raise AddElementError('Port: ' + str(port) + ' out of range')

    def check_port_usage(self, port):
        try:
            self.ports[port]
            raise AddElementError('Port: ' + str(port) + ' is in use')
        except KeyError:
            pass

    def check_element_type(self, element):
        if element.type not in self.accepted_elements:
            raise AddElementError('Element: ' + element.type.name + ' is not valid for ' + self.type.name)
        
    def check_if_element_connected(self, element):
        if element.module_id and element.module_id != self.id and element.type != Et.blind: # roleta moze byc podlaczona 2 razy do jednego modulu - gora i dol
            raise AddElementError('Element: ' + str(element.id) + ' already connected to ' + str(element.module_id))

    def add_element(self, port, element):
        self.check_element_type(element)
        self.check_port_range(port)
        self.check_port_usage(port)
        self.check_if_element_connected(element)

        self.ports[port] = element
        element.reg_id = port
        element.module_id = self.id
        self.elements[element.id] = element


class InputModule(Module):
    """Base class for input modules. It implements read decorator command"""
    types = {Mt.ambient, Mt.input}
    items = {}

    def __init__(self, *args):
        super().__init__(*args)
        InputModule.items[self.id] = self

    @Module.command
    def read(self,):
        regs_values = self.modbus.read_regs(self.id, 0, self.num_of_regs)
        
        if regs_values:  # If transmision was correct
            for element in self.elements.values():
                new_value = regs_values[element.reg_id]
                if new_value != element.value:
                    element.value = new_value
                    element.new_val_flag = True       
            return True
        return False


class OutputModule(Module):
    """ Base class for output modules. It implements write decorator command"""
    types = {Mt.led_light, Mt.output}
    items = {}

    def __init__(self, *args):
        super().__init__(*args)
        OutputModule.items[self.id] = self
        self.values = [0 for _ in range(self.num_of_regs)]  # values to be written in board modbus registers

    @staticmethod
    def write_command(func):
        """Decorator for modbus write commands it checks which elements values differ.
            If the communication result is True it updates elements values """
        @wraps(func)
        def func_wrapper(self):
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


class OutputBoard(OutputModule):

    num_of_ports = 10
    num_of_regs = 10
    accepted_elements = {Et.led, Et.heater, Et.ventilator, Et.blind}
    types = {Mt.output}
    items = {}

    def __init__(self, *args):
        super().__init__(*args)
        OutputBoard.items[self.id] = self

    @Module.command
    @OutputModule.write_command
    def write(self, ):
        return self.modbus.write_coils(self.id, 0, self.values)


class LedLightBoard(OutputModule):
    
    num_of_ports = 3
    num_of_regs = 3
    accepted_elements = {Et.led}
    types = {Mt.led_light}
    items = {}

    def __init__(self, *args):
        super().__init__(args[0], Mt(args[1]), args[2])
        LedLightBoard.items[self.id] = self

    @Module.command
    @OutputModule.write_command
    def write(self, ):
        return self.modbus.write_regs(self.id, 0, self.values)


class AmbientBoard(InputModule):

    num_of_ports = 4
    num_of_regs = 19
    accepted_elements = {Et.ds, Et.dht_hum, Et.dht_temp, Et.ls}
    types = {Mt.ambient}
    items = {}

    def __init__(self, *args):
        InputModule.__init__(self, *args)
        AmbientBoard.items[self.id] = self
        self.ds18b20_counter = 0
    
    def add_element(self, port, element):
        """For Ambient board ports are not the same as registers. ds18b20 sensors are all working on one port"""
        self.check_element_type(element)
        self.check_port_range(port)
        self.check_if_element_connected(element)
        try:
            if self.ports[port]:  # Check if something is already on the port
                if self.ports[port].type == Et.ds:  # If on this port is ds18b20
                    if element.type == Et.ds:   # And user wants to connect another ds18b20
                        pass  # everything is fine
                    else:
                        raise AddElementError('Port: ' + port + ' in use') # raise error
        except KeyError:           
            self.ports[port] = element  # Add element to port

        if element.type == Et.ls:  # dodanie elementu do rejestru
            element.reg_id = 0
        elif element.type == Et.dht_temp:
            element.reg_id = 1
        elif element.type == Et.dht_hum:
            element.reg_id = 2
        elif element.type == Et.ds:
            element.reg_id = 3 + self.ds18b20_counter
            self.ds18b20_counter += 1
       
        element.module_id = self.id
        self.elements[element.id] = element


class InputBoard(InputModule):

    num_of_ports = 15
    num_of_regs = 15
    accepted_elements = {Et.pir, Et.rs, Et.switch}
    types = {Mt.input}
    items = {}

    def __init__(self, *args):
        InputModule.__init__(self, *args)
        InputBoard.items[self.id] = self

        


