from backend.components.base_object import Base_object
from backend.misc.sys_types import et, regt
from dominate.tags import div, button, h4, span, b, p, input, label
from functools import wraps


def field(func):
    @wraps(func) 
    def func_wrapper(*args, **kwargs):
        field = span(cls = "field")
        field_name = div(b(args[0].name), cls = "text-center")
        field_value = func(args[0])
        field.add(field_name, field_value)
        return field
    return func_wrapper

class Visual_element(Base_object):

    table_name = "elements"

    items = {}
    def __init__(self, *args):
        Visual_element.items[args[0]] = self
        if args[0].startswith('r'): #jesli to regulacja. wtedy id jest stringiem i pierwsza litera to r
            super().__init__(args[0], regt(args[1]), args[2]) # inicjalizuj id type, name
        else:
            super().__init__(args[0], et(args[1]), args[2]) # inicjalizuj id type, name
        self.value = 0

    def get_html(self,):
        if self.type == et.blind:
            return self.blind()
        elif self.type in (et.dht_hum, et.dht_temp, et.ds, et.ls):
            return self.value_field()
        elif self.type in (regt.hum, regt.temp):
            return self.input_field()
        elif self.type in (et.heater, et.pir, et.rs, et.switch):
            return self.state_field()
        elif self.type==et.led:
            return self.slider()
        else:
            return self.value()

    @field
    def value_field(self, ):
        return div(str(self.value), cls="field-value value-text text-center", id=str(self.id))

    @field
    def input_field(self, ):
        return input(value=self.value, min="10", max="40", type="number", cls="field-value value-text", id="input" + str(self.id))
    
    @field
    def state_field(self, ):
        st = "off"
        if self.value == '1':
            st = "on"
        elif self.value == '0':
            st = "off"
        return div(cls="field-value field-value-icon "+st, id=str(self.id))
    
    @field
    def value(self, ):
        return span(str(self.value))
   
    @field
    def slider(self,):
       
        range = input(value=self.value, type="range", min="0", max="100",  cls="field-value", id="input" + str(self.id))
        lab = label(str(self.value), id=str(self.id), style="margin-left:5px;")
        return range, lab 

    @field
    def blind(self, ):
        btn_up = input(value='click', type="button", cls='btn btn-md btn-primary', id="input" + str(self.id))
        st = "off"
        if self.value == '1':
            st = "on"
        elif self.value == '0':
            st = "off"
        btn_state = div(cls="field-value field-value-icon "+st, id=str(self.id))      
        return btn_up, btn_state


if __name__ == "__main__":
    btn = get_button(1, name='dupa')
    circle = get_state_ind(2)