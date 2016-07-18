from common.sys_types import et, gt, regt
from common.base_object import Base_object

from dominate.tags import div, br, b, ul, li, span
class Group(Base_object):
    """Grupa agregujaca elementy wizualne"""

    el_to_group_map = {et.blind : gt.blinds,
                       et.dht_hum : gt.ventilation,   # pierwsza grupa jesli czujnik jesli wewnatrz. druga jesli na zewnatrz
                       et.dht_temp: gt.heating,
                       et.ds : gt.heating,
                       et.heater : gt.heating,
                       et.led : gt.lights,
                       et.ls : gt.ambient,
                       et.pir : gt.inputs,
                       et.rs : gt.inputs,
                       et.switch: gt.inputs,
                       et.ventilator : gt.ventilation,
                       regt.hum: gt.ventilation,
                       regt.temp: gt.heating,}

    sensors = ( et.dht_hum, et.dht_temp, et.ds, et.ls)

 

    def __init__(self, type):
        self.type = type
        self.elements = []

    def get_html(self, ):

        gr_name = div(b(self.type.name.title()), cls="panel-heading text-center")
        
        group = div(cls="panel panel-primary")

        group_body = div(cls="panel-body")
        for element in self.elements:
            group_body.add(element.get_html())

        group.add(gr_name, group_body)
        return group




