from common.modules.module import Module
from common.sys_types import mt

class Output_module(Module):
    table_name = 'output_modules'

    def __init__(self, *args):
        super().__init__(*args)

    def write(self, port, value):
        if self.type == mt.output:
            return self.modbus.write_coils(self.id, port, [value])
        elif self.type == mt.led_light:
            return self.modbus.write_coils(self.id, port, [value]) 
    