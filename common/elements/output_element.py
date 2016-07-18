from common.elements.element import Element
from common.sys_types import et
from math import floor

class Output_element(Element):
    table_name = 'output_elements'
  
    types = [et.led, et.heater, et.ventilator, et.blind]
    items = {}

    defualt_priority = 10

    def __init__(self, *args):
        super().__init__(*args)
        Output_element.items[self.id] = self 
        self.desired_value = None
        self.setter_priority = Output_element.defualt_priority   #bardzo niski priorytet. kazy moze go zmienic

    def set_desired_value(self, priority, val):
        if val > 0:
            if priority <= self.setter_priority:
                self.setter_priority = priority
                self.desired_value = val
                return True
        elif val == 0:# przy wylaczeniu kazdy moze ustawic element
            self.setter_priority = Output_element.max_priority
            self.desired_value = 0 
            return False

    def set_value(self,):
        pass

    def __str__(self, ):
        return  "".join([super().__str__(), "\tdesired_value: ", str(self.desired_value), "\tmodule id: ", str(self.module_id), "\tport id: ", str(self.reg_id)])


class Blind(Output_element):
     def __init__(self, *args):
        super().__init__(*args)
        
        self.module_id_up = floor(self.module_id/16)
        self.module_id_down = self.module_id%16
        self.reg_up    = floor(self.reg_id/16)
        self.reg_down  = self.reg_id%16
if __name__ == "__main__":
    pass


