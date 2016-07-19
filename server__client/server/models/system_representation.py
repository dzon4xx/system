from sys_database.database import create_db_object

from server__client.server.models.room import Room
from server__client.server.models.group import Group
from server__client.server.models.visual_element import *

from common.sys_types import rt, et
from common.relations.regulation import Regulation

def load_system_representation():
    db = create_db_object() #database object
    db.load_objects_from_table(Room)
    #rooms_data = db.get_table(Room)

    for room in Room.items.values():
        if room.elements: # if there are elments in room
            room.elements = [db.read(Visual_element, 'id', int(el_num)) for el_num in room.elements.split(',')]
        else:
            room.elements = [] # so the type of room.elements is always list
        if room.regulations: # if there are regulations in room
            regulations = room.regulations
            room.regulations = []
            for reg_id in regulations.split(','):
                reg_data = db.read_simple(Regulation.table_name, 'id', int(reg_id))
                reg_data[0] = 'r'+str(reg_data[0]) #dodanie litery r do id zeby bylo wiadomo ze chodzi o wartosc nastawy regulacji
                room.regulations.append(Visual_element(*reg_data[:3]))
        else:
            room.regulations = []

        for el in room.elements: # Adds elements to groups and groups to rooms
            group_type = Group.el_to_group_map[el.type]
            group = Group(group_type)
            if group_type not in room.groups.keys():
                room.groups[group_type] = group
                group.elements.append(el)
            else:
                room.groups[group_type].elements.append(el)

        #room.add_element(*room_data[Room.COL_ELS])
    pass


if __name__ == "__main__":
    load_system_representation()