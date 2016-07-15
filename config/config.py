import sys

from server__client.server.models.user import User
from common.elements.element import Element
from common.elements.input_element import Input_element
from common.elements.output_element import Blind, Output_element
from common.modules.input_module import Input_module, Ambient_module
from common.modules.output_module import Output_module 
from common.modules.module import Module, Add_element_error

from server__client.server.models.room import Room

from common.relations.dependancy import Dependancy, Dependancy_config_error
from common.relations.regulation import Regulation, Regulation_config_error

from common.sys_types import mt, et, rt, regt, gt

from common.color_logs import color_logs

from sys_database.database import Database

import logging

class System_creator():
    
    def __init__(self, logger, db):
        self.db = db
        self.logger = logger
        self.room_id    = 0
        self.element_id = 0
        self.module_id  = 0
        self.dependancy_id = 0
        self.regulation_id = 0
     
    def create_tables(self, ):

        self.db.create_tables(Element,
                             Input_element,                               
                             Output_element, 
                             Input_module, 
                             Output_module, 
                             Room,
                             Dependancy,
                             Regulation, 
                             User)

    def get_rooms(self):
        """Zwraca pokoje razem z elementami wejsciowymi i wyjsciowymi"""

        rooms_table = self.db.get_table(Room)
        elements_table = self.get_table(Element)

        rooms=[]
        for room_data in rooms_table:
            rooms.append(Room(*room_data))

    def get_modules(self,):
        """Zwraca moduly wejsciowe i wyjsciowe w systemie"""

        modules_table = self.db.get_table(Module)
        elements_table = self.db.get_table(Element)

        input_modules = []
        output_modules = []
        #Odzyskaj moduly z bazy danych
        for module_data in modules_table:
            modules_data[1] = mt(modules_data[1]) # Typ jako enum
            if module_data[1] in Module.input_modules:
                input_modules.append(Module(*module_data))

            elif module_data[1] in Module.output_modules:
                output_modules.append(Module(*module_data))

        #Odzyskaj elementy z bazy danych i przypisz je modulom
        for element_data in elements_table:
            element_type = et(element_data[Element.TYPE])
            element_module_id = element_data[Element.MODULE]
            if element.type in Element.input_elements:
                for module in input_modules:
                    if element_module_id == module.id:
                        element_data[Element.TYPE]
                        element = Element(element_data)
                        module.add_element(element, element.port)

        return [input_modules, output_modules]

    def add_room(self, type = None, name = ''):      
        room = Room(self.room_id ,type, name)
        self.room_id += 1
        self.logger.info('Created room: ' + str(room))

    def add_module(self, type = None, name = ''):
     
        if type in Module.input_modules:
            if type == mt.ambient:
                module = Ambient_module(self.module_id, type, name)
            else:
                module = Input_module(self.module_id, type, name)
        else:
            module = Output_module(self.module_id, type, name)
        self.module_id += 1       
        self.logger.info('Created module: ' + str(module))
              
    def add_element(self, type = None, name = '', room_id = None, module_id = None, port = None,):

        if name == '':
            name = 'element ' + str(Element.ID)

        try:
            if type == et.dht:
                el1= Input_element(self.element_id, et.dht_hum, 'Humidity')
                self.element_id += 1
                el2 = Input_element(self.element_id, et.dht_temp, 'Temperature')
                self.element_id += 1
                Module.items[module_id].add_element(port, el1)
                Module.items[module_id].add_element(port, el2)
                Room.items[room_id].add_element(el1, el2)

            elif type == et.blind:
                blind_ports   = (port[0]<<4) + port[1]    # kodowanie w jednej liczbie dwoch portow
                blind_modules = (module_id[0]<<4) + module_id[1] # kodowanie w jednej liczbie dwoch modulow
                el = Blind(self.element_id, et.blind, name, blind_modules, blind_ports)
                self.element_id += 1
                Room.items[room_id].add_element(el)
                Module.items[module_id[0]].add_element(port[0], el)
                Module.items[module_id[1]].add_element(port[1], el)

            elif type in Input_element.types:
                el = Input_element(self.element_id, type, name)
                self.element_id += 1
                Room.items[room_id].add_element(el)
                Module.items[module_id].add_element(port, el)

            elif type in Output_element.types:
                el = Output_element(self.element_id, type, name, module_id, port)
                self.element_id += 1
                Room.items[room_id].add_element(el)
                Module.items[module_id].add_element(port, el)

        except Add_element_error as e:
            self.logger.warn(e.msg)
           
        else:         
            self.logger.info("Created element: " + type.name + "\troom: " + str(room_id) + "\tmodule: " + str(module_id))

    def add_dependancy(self, name, dependancy_str):

        if name == '':
            name = 'dependancy ' + str(Dependancy.ID)

        try:
            Dependancy(self.dependancy_id, name, dependancy_str)
            self.dependancy_id += 1
        except Dependancy_config_error as e:
            self.logger.warn(e.msg)

    def add_regulation(self, name = '', feed_el_id = None, out_el_id = None, set_point = None, dev = None):
        
        if Element.items[feed_el_id].type == et.ds or et.dht_temp:
             reg_type = regt.temp
             assert Element.items[out_el_id].type == et.heater

        elif Element.items[feed_el_id].type == et.dht_hum:
             reg_type = regt.hum
             assert Element.items[out_el_id].type == et.ventilator

        if name == '':
            name = 'regulation ' + str(Regulation.ID)
        try:
            Regulation(self.regulation_id, reg_type, name, out_el_id, feed_el_id, set_point, dev)

            for room in Room.items.values(): # przypisz regulacje do pokoju w ktorym znajduje sie odpowiadajacy jej el wyjsciowy
                for el in room.elements:
                    if el.id == out_el_id:
                        room.regulations.append(self.regulation_id) 

            self.regulation_id += 1
        except Regulation_config_error as e:
            self.logger.warn(e.msg)

    def save(self,):
        self.__save_dependancies()
        self.__save_elements()
        self.__save_modules()
        self.__save_regulations()
        self.__save_rooms()

    def __save_modules(self, ):
        for module in Module.items.values():
            if module.type == mt.ambient:
                self.db.save(Input_module, (module.id, module.type.value, module.name, ",".join([str(element.id) for element in module.regs if (element != None)])))
            
            elif module.type in Module.input_modules:
                self.db.save(Input_module, (module.id, module.type.value, module.name, ",".join([str(element.id) for element in module.ports if (element != None)])))
            
            elif module.type in Module.output_modules:
                self.db.save(Output_module, (module.id, module.type.value, module.name,))
            
    def __save_rooms(self, ):
        for room in Room.items.values():
            els = ",".join([str(element.id) for element in room.elements])
            regs = ",".join([str(regulation_id) for regulation_id in room.regulations])
            self.db.save(Room, (room.id, room.type.value, room.name, els, regs))

    def __save_elements(self, ):
        for element in Element.items.values():
            self.db.save(Element, (element.id, element.type.value, element.name))
            if element.type in Input_element.types:
                self.db.save(Input_element, (element.id, element.type.value, element.name))
            elif element.type in Output_element.types:
                self.db.save(Output_element, (element.id, element.type.value, element.name, element.module_id, element.port))

    def __save_dependancies(self, ):
        for dep in Dependancy.items.values():
            self.db.save(Dependancy, (dep.id, dep.name, dep.dep_str,))

    def __save_regulations(self, ):
        for reg in Regulation.items.values():
            self.db.save(Regulation, (reg.id, reg.type.value, reg.name, reg.feed_el_id, reg.out_el_id, reg.set_point, reg.dev))


color_logs()

root = sys.path[-1]
db_path =  "\\".join([root, 'sys_database', "sys_database.db"])

conf_logger = logging.getLogger('CONF')
db_logger = logging.getLogger('DB')
db_logger.disabled = False
db_logger.setLevel(logging.DEBUG)

system = System_creator(conf_logger, Database(db_path, db_logger))

system.create_tables()

print("\n")

system.add_module(mt.input, 'Input')           # 0
system.add_module(mt.output, 'Output')         # 1
system.add_module(mt.led_light, 'Led light')   # 2
system.add_module(mt.ambient, 'Ambient')       # 3

print("\n")

system.add_room(type=rt.wc, name='Water Closet') # 0
system.add_room(type=rt.sleeping_room, name='Parent\'s sleeping room')       # 1
system.add_room(type=rt.sleeping_room, name='Johny\'s sleeping room')       # 2
system.add_room(type=rt.corridor, name='Main corridor')     # 3
system.add_room(type=rt.living_room, name='Living room')  # 4
system.add_room(type=rt.kitchen, name='Kitchen')      # 5
system.add_room(type=rt.outside, name='Outside')      # 6

print("\n")

# id 0
system.add_element(type = et.dht, 
                    name = 'Humidity and temperature',
                    room_id = 0,
                    module_id = 3,
                    port =   0)#0,1
system.add_element(type = et.led, 
                    name = 'Led strip',
                    room_id = 0,
                    module_id = 2,
                    port =   0)#2
system.add_element(type = et.pir, 
                    name = 'Motion',
                    room_id = 0,
                    module_id = 0,
                    port =   0)#3

# id 1
system.add_element(type = et.ds, 
                    name = 'Temperature',
                    room_id = 1,
                    module_id = 3,
                    port =   1)#4
system.add_element(type = et.heater, 
                    name = 'Heater',
                    room_id = 1,
                    module_id = 1,
                    port =   0)#5
system.add_element(type = et.blind, 
                    name = 'Blind',
                    room_id = 1,
                    module_id = [1, 1],
                    port =   [1, 2])#6
system.add_element(type = et.pir, 
                    name = 'Motion',
                    room_id = 1,
                    module_id = 0,
                    port =   1)#7
system.add_element(type = et.rs, 
                    name = 'RS window',
                    room_id = 1,
                    module_id = 0,
                    port =   2)#8

# id 2
system.add_element(type = et.ds, 
                    name = 'Temperature',
                    room_id = 2,
                    module_id = 3,
                    port =   1)#9
system.add_element(type = et.heater, 
                    name = 'Heater',
                    room_id = 2,
                    module_id = 1,
                    port =   3)#10
system.add_element(type = et.led, 
                    name = 'Led strip',
                    room_id = 2,
                    module_id = 2,
                    port =   1)#11

# id 3
system.add_element(type = et.ds, 
                    name = 'Temperature',
                    room_id = 3,
                    module_id = 3,
                    port =   1)#12
system.add_element(type = et.pir, 
                    name = 'Motion',
                    room_id = 3,
                    module_id = 0,
                    port =   3)#13

# id 4
system.add_element(type = et.ds, 
                    name = 'Temperature',
                    room_id = 4,
                    module_id = 3,
                    port =   1)#14
system.add_element(type = et.heater, 
                    name = 'Heater',
                    room_id = 4,
                    module_id = 1,
                    port =   4)#15
system.add_element(type = et.led, 
                    name = 'Led strip',
                    room_id = 4,
                    module_id = 2,
                    port =   2)#16
system.add_element(type = et.blind, 
                    name = 'Blind',
                    room_id = 4,
                    module_id = [1, 1],
                    port =   [5, 6])#17

system.add_element(type = et.pir, 
                    name = 'Motion',
                    room_id = 4,
                    module_id = 0,
                    port =   4)#18
system.add_element(type = et.rs, 
                    name = 'RS window',
                    room_id = 4,
                    module_id = 0,
                    port =   5)#19

# id 5
system.add_element(type = et.ds, 
                    name = 'Temperature',
                    room_id = 5,
                    module_id = 3,
                    port =   1)#20
system.add_element(type = et.heater, 
                    name = 'Heater',
                    room_id = 5,
                    module_id = 1,
                    port =   7)#21
system.add_element(type = et.blind, 
                    name = 'Blind',
                    room_id = 5,
                    module_id = [1, 1],
                    port =   [8, 9])#22

system.add_element(type = et.pir, 
                    name = 'Motion',
                    room_id = 5,
                    module_id = 0,
                    port =   6)#23
system.add_element(type = et.rs, 
                    name = 'RS Window',
                    room_id = 5,
                    module_id = 0,
                    port =   7)#24

#id 6
system.add_element(type = et.ds, 
                    name = 'Temperature',
                    room_id = 6,
                    module_id = 3,
                    port =   1)#25
system.add_element(type = et.ls, 
                    name = 'Light level',
                    room_id = 6,
                    module_id = 3,
                    port =   2)#26
system.add_element(type = et.rs, 
                    name = 'RS Main doors',
                    room_id = 6,
                    module_id = 0,
                    port =   8)#27

system.add_dependancy('wlaczanie swiatla w lazience', '[e3=1] then e2=100; e2=0{100};')
system.add_dependancy('Zaleznosc 2', '[d=mon,tue,wed,thu,fri] and [t=5:50] then e2=20{0}; e2=0{200}; e5=1{0}')
system.add_regulation('Temp set', feed_el_id=0, out_el_id=10, set_point=20, dev=2)
print("\n")
system.save()

print("\n")

for module in Module.items.values():
    print(str(module))
print("\n")

for room in Room.items.values():
    print(str(room))

print("\n")

for element in Element.items.values():
    print(str(element))
 
print("\n")
     
for dep in Dependancy.items.values():
    print(str(dep))

print("\n")

for reg in Regulation.items.values():
    print(str(reg))

