from common.base_object import Base_object
from tornado import template
import tornado.web
from dominate.tags import div, br, h3

class Room(Base_object):
    """Defines room in system"""
    table_name = 'rooms'
    column_headers_and_types = Base_object.column_headers_and_types + [['els', 'text'], ['regs', 'text']]
    
    COL_ELS = 3                                     
    ID = 0
    items = {}
    groups_per_row = 3

    def __init__(self, *args):
        super().__init__(*args) # inicjalizuj id type, name
        Room.items[self.id] = self
        self.elements = []
        self.regulations = []
        self.groups = {}


    def add_element(self, *elements):
        for element in elements:
            self.elements.append(element)

    def get_display_data(self,):
        rows = []
        row = []
        for group_num, group in enumerate(self.groups.values()):
            row.append(group)
            if group_num == Room.groups_per_row-1:
                rows.append(row)
                row = []
        if row:
            rows.append(row) # dla ostatniego niepelnego rzedu

        return rows

    def get_html(self, ):

        rows = self.get_display_data()

        room_container = div(cls = "well", id='room' + str(self.id))
        room_name = h3(self.name, style="text-align: center")
        room_container.add(room_name)
        for row in rows:            
            r = div(cls='row')
            with r:
                for group in row:
                    div(cls="col-lg-4 group").add(group.get_html())
            room_container.add(r)
        return room_container.render()


    def __str__(self, ):
        return "".join([super().__str__(), '\tELEMENTS: ',  ",".join([str(el.id) for el in self.elements])])

if __name__ == "__main__":
    from common.sys_types import rt, et
    from common.elements.output_element import Blind
    room = Room(rt.corridor, 'Korytarz') 
    el0 = Blind(et.blind, 'roleta', 86, 86)
    el1 = Blind(et.blind, 'roleta', 86, 86)
    room.add_element((el0, el1))
    print (str(room))
