from common.modules.input_module import Input_module, Module
from common.sys_types import et


class Anfa_ambient(Input_module):

    number_of_regs = 19

    DS_ID = 0

    def __init__(self, *args):
        Input_module.__init__(self, *args)
        self.regs = self.__create_regs()

    def read(self,):
        pass

    def __create_regs(self):
        return [None for num in range(Module.num_of_regs_ambient)]

    def add_element(self, port, element):
        """For anfa ambient ports are not the same as registers. ds18b20 sensors are all working on one port"""
        self.check_element_type(element)
        self.check_port_range(port)
        self.check_if_element_connected(element)

        if self.ports[port]:    #jesli cos juz jest na porcie
            if self.ports[port].type == et.ds:  # jesli w na tym porcie juz jest ds 
                if element.type == et.ds:
                    pass
                else:
                    raise Add_element_error('Port: ' + port + ' in use')
            
        self.ports[port] = element # dodawanie elementu do portu

        if element.type == et.ls: # dodanie elementu do rejestru
            self.regs[0] = element
        elif element.type == et.dht_hum:
            self.regs[1] = element
        elif element.type == et.dht_hum:
            self.regs[2] = element
        elif element.type == et.ds:
            self.regs[3 + Anfa_ambient.DS_ID] = element
            Anfa_ambient.DS_ID += 1

        element.module_id = self.id





