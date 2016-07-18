from common.modules.module import Module
from common.sys_types import mt

class Output_module(Module):
    table_name = 'output_modules'

    items = {}
    def __init__(self, *args):
        super().__init__(*args)
        Output_module.items[self.id] =  self

    def write(self, port, value):
        if self.type == mt.output:
            return self.modbus.write_coils(self.id, port, [value])
        elif self.type == mt.led_light:
            return self.modbus.write_coils(self.id, port, [value]) 
    