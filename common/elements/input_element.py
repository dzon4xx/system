from common.elements.element import Element
from common.sys_types import et

class Input_element(Element):
    table_name = "input_elements"
    COL_OUT_ELS = 3 #numery kolumn
    
    types = [et.ds, et.dht_hum, et.dht_temp, et.pir, et.rs, et.ls]
    items = {}

    def __init__(self, *args):
        """arguments: type name """
        super().__init__(*args) # inicjalizuj type, name
        Input_element.items[self.id] = self       


    def __str__(self, ):
        return  "".join([super().__str__(), "\tvalue:\t", str(self.value)])


