from common.modules.module import Module
from common.sys_types import mt

class Input_module(Module):
    table_name = 'input_modules'

    items = {}
    def __init__(self, *args):
        super().__init__(*args)
        Input_module.items[self.id] =  self

        self.read_freq = None

    def read(self,):
        self.tran_num += 1 #
        if self.type == mt.ambient:
            regs = self.modbus.read_regs(self.id, 0, Module.num_of_regs_ambient)

        elif self.type == mt.input:
            regs = self.modbus.read_regs(self.id, 0, Module.num_of_ports[mt.input])

        if regs:    # if there is response from module
            self.correct_trans_num += 1
            for reg_num, reg in enumerate(regs): 
                try:
                    self.regs[reg_num].value = reg
                except KeyError:
                    pass
            return True
        else:
            self.available = False
            self.courupted_trans_num += 1
            #TODO notification about module failures
            return False

        

