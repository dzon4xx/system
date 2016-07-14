from common.modules.module import Module,  Add_element_error
from common.sys_types import et

class Input_module(Module):
    table_name = 'input_modules'
    column_headers_and_types = Module.column_headers_and_types + [['input_elements', 'text']]
     

    def __init__(self, *args):
        super().__init__(*args)
        self.in_elements = []

class Ambient_module(Input_module):

    number_of_regs = 19

    DS_ID = 0

    def __init__(self, *args):
        super().__init__(*args)
        self.regs = self.__create_regs()

    def add_element(self, port, element):
        self.check_element_type(element)
        self.check_port_range(port)
        self.check_if_element_connected(element)
        if self.ports[port]:    #jesli cos juz jest na porcie
            if self.ports[port].type == et.ds:  # jesli w na tym porcie juz jest ds 
                if element.type == et.ds:
                    pass
                else:
                    raise Add_element_error('Port: ' + port + ' in use')
            
        self.ports[port] = element

        if element.type == et.ls:
            self.regs[0] = element
        elif element.type == et.dht_hum:
            self.regs[1] = element
        elif element.type == et.dht_hum:
            self.regs[2] = element
        elif element.type == et.ds:
            self.regs[3 + Ambient_module.DS_ID] = element
            Ambient_module.DS_ID += 1

        element.module_id = self.id

    def __create_regs(self):
        return [None for num in range(self.number_of_regs)]