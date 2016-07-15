from common.base_object import Base_object
from common.sys_types import et
from dominate.tags import div, button, h4, span, b, p


class Visual_element(Base_object):

    table_name = "elements"

    items = {}
    def __init__(self, *args):
        Visual_element.items[args[0]] = self
        super().__init__(args[0], et(args[1]), args[2]) # inicjalizuj id type, name
        self.value = None

    def get_html(self,):
        if self.type == et.blind:
            return self.get_blind()
        #elif self.type in (et.dht_hum, et.dht_temp, et.ds, et.ls):
        #    return self.get_value_field()
        else:
            return self.get_value()

    def get_value(self, ):
        name = span(b(self.name))
        val = span(str(self.value))
        colon = span(':')
        return name, colon, val


    def get_blind(self, ):
        
        btn_name = p(b(self.name), cls="text-center")

        btn_up = button('up', cls='btn-lg btn-default')
        btn_up['onclick'] = self.send_function(100)
        btn_down = button('down', cls='btn-lg btn-default')
        btn_down['onclick'] = self.send_function(0)
        btn_group = div(btn_name, btn_up, btn_down, cls="blind")
        return btn_group


    def send_function(self, val):
        val = ','.join([str(self.id), str(val)])
        val = "\"" + val + "\""
        fun = 'ws.send' + self._brackets(val)
        return fun
    def _brackets(self, str):
        return '(' + str + ')'


    def get_input(self, ):
        html= tag('span', atr="""class="fa fa-circle\"""", inner=self.value)







if __name__ == "__main__":
    btn = get_button(1, name='dupa')
    circle = get_state_ind(2)