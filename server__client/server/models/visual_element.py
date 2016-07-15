from common.base_object import Base_object
from common.sys_types import et, regt
from dominate.tags import div, button, h4, span, b, p, input, label
from functools import wraps


def field(func):
    @wraps(func) 
    def func_wrapper(*args, **kwargs):
        field = div(cls = "field")
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
        if isinstance(args[0], str): #jesli to regulacja. wtedy id jest stringiem i pierwsza litera to r
            super().__init__(args[0], regt(args[1]), args[2]) # inicjalizuj id type, name
        else:
            super().__init__(args[0], et(args[1]), args[2]) # inicjalizuj id type, name
        self.value = None

    def get_html(self,):
        if self.type == et.blind:
            return self.blind()
        elif self.type in (et.dht_hum, et.dht_temp, et.ds, et.ls):
            return self.value_field()
        elif self.type in (regt.hum, regt.temp):
            return self.input_field()
        elif self.type in (et.heater, et.pir, et.rs,):
            return self.state_field()
        elif self.type==et.led:
            return self.slider()
        else:
            return self.value()

    @field
    def value_field(self, ):
        return div(str(self.value), cls="field-value field-value-text text-center")

    @field
    def input_field(self, ):
        return input(str(self.value), type="number", cls="field-value field-value-text text-center", id="input" + str(self.id))
    
    @field
    def state_field(self, ): 
        return div(cls="field-value field-value-icon on")
    
    @field
    def value(self, ):
        return span(str(self.value))

    def nothing(self, ):
        return span()
    
    @field
    def slider(self,):
        slider = div(cls="slider")
        range = input( type="range", min="0", max="100",  cls="field-value", id="inpute" + str(self.id))
        lab = label(str(self.value), id="e" + str(self.id), style="margin-left:5px;")
        slider.add(range, lab)
        return slider

    @field
    def blind(self, ):
        btn_up = button('up', cls='btn-lg btn-default', onclick = self.__send_function(100))
        btn_down = button('down', cls='btn-lg btn-default', onclick = self.__send_function(0))         
        return btn_up, btn_down

    def __send_val(self, ):
        return self.__send_function("$(#input"  + str(self.id)+")" + ".val()")

    def __send_function(self, val):
        id = 'e' + str(self.id)
        send = ','.join([id, str(val)])
        send = "\"" + send + "\""
        fun = 'ws.send' + self.__brackets(send) + ";"
        return fun

    def __brackets(self, str):
        return '(' + str + ')'


    def get_input(self, ):
        html= tag('span', atr="""class="fa fa-circle\"""", inner=self.value)



def save_create(func):
    """Handles connection commit eventual rollback and closing while saving or creating to database"""
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if args[0].connect():
            try:
                args[0].cur = args[0].con.cursor()            
                return func(*args, **kwargs)               
            except sql.Error as e:
                args[0].con.rollback()               
                args[0].logger.exception( "DATABASE SAVE/CREATE Error %s:",  e.args[0])
                pass
            finally:
                args[0].con.commit() 
                args[0].close()
        else:
            pass
    return func_wrapper



if __name__ == "__main__":
    btn = get_button(1, name='dupa')
    circle = get_state_ind(2)