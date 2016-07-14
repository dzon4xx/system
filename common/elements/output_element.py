from common.elements.element import Element
from common.sys_types import et
from math import floor

class Output_element(Element):

    table_name = 'output_elements'

    COL_MODULE_ID, COL_PORT,  = 3, 4, #numery kolumn
    column_headers_and_types = Element.column_headers_and_types + [['module_id', 'integer'], ['port', 'integer']] 
                                

    types = [et.led, et.heater, et.ventilator, et.blind]
    items = {}

    max_priority = 10

    def __init__(self, *args):
        super().__init__(*args[:Output_element.COL_MODULE_ID])
        Output_element.items[self.id] = self 
        self.desired_value = None
        self.setter_priority = Output_element.max_priority   #bardzo niski priorytet. kazy moze go zmienic
        self.module_id = args[Output_element.COL_MODULE_ID]
        self.port = args[Output_element.COL_PORT]
        

        

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
        return  "".join([super().__str__(), "\tdesired_value: ", str(self.desired_value), "\tmodule id: ", str(self.module_id), "\tport id: ", str(self.port)])


class Blind(Output_element):
     def __init__(self, *args):
        super().__init__(*args)
        
        self.module_id_up = floor(self.module_id/16)
        self.module_id_down = self.module_id%16
        self.port_up    = floor(self.port/16)
        self.port_down  = self.port%16
if __name__ == "__main__":
    pass












































#class Cause_effect_element(Output_element):
    
#    table_name = 'cause_effect_elements'

#    column_headers_and_types = Output_element.column_headers_and_types + [ ['causes', 'text'], ['efects', 'text']] 
                                                                  
#    CAUSES, EFECTS = 5, 6 #numery kolumn

#    def __init__(self, *args):
#        super().__init__(*args[:Cause_effect_element.CAUSES-1])
#        self.causes = args[Cause_effect_element.CAUSES-1]
#        self.efects = args[Cause_effect_element.EFECTS-1]

#    def __str__(self, ):
#        return  "".join([super().__str__(), "\tcauses: ", str(self.causes), "\tefects: ", str(self.efects)])

#class Regulated_element(Output_element):

#    table_name = 'regulated_elements'

#    column_headers_and_types = Output_element.column_headers_and_types + [ ['feed_el', 'integer'], ['set_point', 'integer']]
    
#    FEED_EL, SET_POINT = 5, 6 #numery kolumn 

#    def __init__(self, *args):
#        super().__init__(*args[:Regulated_element.FEED_EL-1])
#        self.feed_el = args[Regulated_element.FEED_EL-1]
#        self.set_point = args[Regulated_element.SET_POINT-1]

#    def __str__(self, ):
#        return  "".join([super().__str__(), "\tfeed_el: ", str(self.feed_el), "\tset_point: ", str(self.set_point)])


