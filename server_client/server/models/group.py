from backend.misc.sys_types import Et, Gt, Regt
from backend.components.base_component import BaseComponent

from dominate.tags import div, br, b, ul, li, span
class Group(BaseComponent):
    """Groups aggregate visual elements"""

    el_to_group_map = {Et.blind : Gt.blinds,
                       Et.dht_hum : Gt.ventilation,  # pierwsza grupa jesli czujnik jesli wewnatrz. druga jesli na zewnatrz
                       Et.dht_temp: Gt.heating,
                       Et.ds : Gt.heating,
                       Et.heater : Gt.heating,
                       Et.led : Gt.lights,
                       Et.ls : Gt.ambient,
                       Et.pir : Gt.inputs,
                       Et.rs : Gt.inputs,
                       Et.switch: Gt.inputs,
                       Et.ventilator : Gt.ventilation,
                       Regt.hum: Gt.ventilation,
                       Regt.temp: Gt.heating,}

    sensors = (Et.dht_hum, Et.dht_temp, Et.ds, Et.ls)

 

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




