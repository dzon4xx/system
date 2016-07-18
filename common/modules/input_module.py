from common.modules.module import Module
from common.sys_types import mt

class Input_module(Module):
    table_name = 'input_modules'
     
    def __init__(self, *args):
        super().__init__(*args)

        self.read_freq = None

    def read(self,):

        if self.type == mt.ambient:
            regs = self.modbus.read_regs(self.id, 0, Module.num_of_regs_ambient)

        elif self.type == mt.input:
            regs = self.modbus.read_regs(self.id, 0, Module.num_of_ports[mt.input])

        if regs:    # if there is response from module
            for reg_num, reg in enumerate(regs): 
                try:
                    self.ports[reg_num].value = reg
                except KeyError:
                    pass
            return True
        else:
            #TODO notification about module failures
            return False

        

