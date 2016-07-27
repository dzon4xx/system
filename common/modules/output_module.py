from common.modules.module import Module
from common.sys_types import mt

class Output_module(Module):
    table_name = 'output_modules'

    num_of_ports = {mt.led_light: 3,
                 mt.output : 10}

    items = {}
    def __init__(self, *args):
        super().__init__(*args)
        Output_module.items[self.id] =  self
        self.regs_values = [0 for i in range(Output_module.num_of_ports[self.type])]

    def write(self, ):
        if self.type == mt.output:
            return self.modbus.write_coils(self.id, 0, self.regs_values)
        elif self.type == mt.led_light:
            return self.modbus.write_coils(self.id, 0, self.regs_values) 
    