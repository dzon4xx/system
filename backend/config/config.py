import sys
import logging

from backend.components.elements.element import Element, Input_element, Output_element, Blind

from backend.components.modules.module import Module, Anfa_output, Anfa_led_light, Anfa_ambient, Anfa_input, Add_element_error

from backend.components.relations.dependancy import Dependancy, Dependancy_config_error
from backend.components.relations.regulation import Regulation, Regulation_config_error
from server__client.server.models.room import Room
from server__client.server.models.user import User

from backend.misc.sys_types import mt, et, rt, regt, gt
from backend.misc.color_logs import color_logs

from backend.sys_database.database import Database, create_db_object

class System_creator():
    
    def __init__(self):
        self.db = create_db_object()
        self.db.logger.disabled = True
        self.logger = logging.getLogger('CONF')
        self.room_id    = 0
        self.element_id = 0
        self.module_id  = 1 # address 0 is a broadcast address in modbus. Therfore id starts from 1
        self.dependancy_id = 0
        self.regulation_id = 0
     
    def create_tables(self, ):

        self.db.create_tables(Element,
                              Blind,
                             Module, 
                             Room,
                             Dependancy,
                             Regulation, )

    def delete_tables(self, ):
            self.db.delete_tables(Element,
                             Blind,
                             Module, 
                             Room,
                             Dependancy,
                             Regulation, )

    def add_room(self, type = None, name = ''):      
        room = Room(self.room_id ,type, name, [], [])
        self.room_id += 1
        self.logger.info('Created room: ' + str(room))

    def add_module(self, type = None, name = ''):
     
        if type == mt.ambient:
            module = Anfa_ambient(self.module_id, type, name)
        elif type == mt.input:
            module = Anfa_input(self.module_id, type, name)
        elif type == mt.output:
            module = Anfa_output(self.module_id, type, name)
        elif type == mt.led_light:
            module = Anfa_led_light(self.module_id, type, name)

        self.module_id += 1       
        self.logger.info('Created module: ' + str(module))
              
    def add_element(self, type = None, name = '', room_id = None, module_id = None, port = None,):

        if name == '':
            name = 'element ' + str(Element.ID)

        try:
            if type == et.dht:
                el1= Element(self.element_id, et.dht_hum, 'Humidity', module_id, port)
                self.element_id += 1
                el2 = Element(self.element_id, et.dht_temp, 'Temperature', module_id, port)
                self.element_id += 1
                Module.items[module_id].add_element(port, el1)
                Module.items[module_id].add_element(port, el2)
                Room.items[room_id].add_element(el1, el2)

            elif type == et.blind:

                blind_up = Blind(self.element_id, et.blind, name, module_id[0], port[0], 'up', None)
                self.element_id += 1
                blind_down = Blind(self.element_id, et.blind, name, module_id[1], port[1], 'down', None)
                self.element_id += 1

                blind_up.other_blind = blind_down.id
                blind_down.other_blind = blind_up.id
                
                Room.items[room_id].add_element(blind_up, blind_down)
                Module.items[module_id[0]].add_element(port[0], blind_up)
                Module.items[module_id[1]].add_element(port[1], blind_down)

            elif type in Input_element.types:
                el = Input_element(self.element_id, type, name, module_id, port)
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

        else:
            raise Regulation_config_error('REGULATION ERROR Feed element: ' + (feed_el_id) + " not in defined input elements")

        if name == '':
            name = 'regulation ' + str(Regulation.ID)
        try:
            Regulation(self.regulation_id, reg_type, name, feed_el_id, out_el_id, set_point, dev)

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
            self.db.save(Module, (module.id, module.type.value, module.name, ))            
                       
    def __save_rooms(self, ):
        for room in Room.items.values():
            els = ",".join([str(element.id) for element in room.elements])
            regs = ",".join([str(regulation_id) for regulation_id in room.regulations])
            self.db.save(Room, (room.id, room.type.value, room.name, els, regs))

    def __save_elements(self, ):
        for element in Element.items.values():
            self.db.save(Element, (element.id, element.type.value, element.name, element.module_id, element.reg_id))
        for blind in Blind.items.values():           
            self.db.save(Blind, (blind.id, blind.type.value, blind.name, blind.module_id, blind.reg_id, blind.direction, blind.other_blind))

    def __save_dependancies(self, ):
        for dep in Dependancy.items.values():
            self.db.save(Dependancy, (dep.id, dep.name, dep.dep_str,))

    def __save_regulations(self, ):
        for reg in Regulation.items.values():
            self.db.save(Regulation, (reg.id, reg.type.value, reg.name, reg.feed_el_id, reg.out_el_id, reg.set_point, reg.dev))


color_logs()

system = System_creator()
system.logger.setLevel('DEBUG')

system.create_tables()

print("\n")

system.add_module(mt.input, 'Input')           # 1
system.add_module(mt.output, 'Output')         # 2
system.add_module(mt.led_light, 'Led light')   # 3
system.add_module(mt.ambient, 'Ambient')       # 4

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
                    module_id = 4,
                    port =   0)#0,1
system.add_element(type = et.led, 
                    name = 'Led strip',
                    room_id = 0,
                    module_id = 3,
                    port =   0)#2
system.add_element(type = et.pir, 
                    name = 'Motion',
                    room_id = 0,
                    module_id = 1,
                    port =   0)#3
system.add_element(type = et.switch,
                   name = 'Switch',
                   room_id = 0,
                   module_id = 1,
                   port = 9)#4

# id 1
system.add_element(type = et.ds, 
                    name = 'Temperature',
                    room_id = 1,
                    module_id = 4,
                    port =   1)#5
system.add_element(type = et.heater, 
                    name = 'Heater',
                    room_id = 1,
                    module_id = 2,
                    port =   0)#6
system.add_element(type = et.blind, 
                    name = 'Blind',
                    room_id = 1,
                    module_id = [2, 2],
                    port =   [1, 2])#7 8
system.add_element(type = et.pir, 
                    name = 'Motion',
                    room_id = 1,
                    module_id = 1,
                    port =   1)#9
system.add_element(type = et.rs, 
                    name = 'RS window',
                    room_id = 1,
                    module_id = 1,
                    port =   2)#10
system.add_element(type = et.switch,
                   name = 'Switch',
                   room_id = 1,
                   module_id = 1,
                   port = 10)#11

# id 2
system.add_element(type = et.ds, 
                    name = 'Temperature',
                    room_id = 2,
                    module_id = 4,
                    port =   1)#12
system.add_element(type = et.heater, 
                    name = 'Heater',
                    room_id = 2,
                    module_id = 2,
                    port =   3)#13
system.add_element(type = et.led, 
                    name = 'Led strip',
                    room_id = 2,
                    module_id = 3,
                    port =   1)#14
system.add_element(type = et.switch,
                   name = 'Switch',
                   room_id = 2,
                   module_id = 1,
                   port = 11)#15
system.add_element(type = et.pir, 
                    name = 'Motion',
                    room_id = 2,
                    module_id = 1,
                    port =   14)#16

# id 3
system.add_element(type = et.ds, 
                    name = 'Temperature',
                    room_id = 3,
                    module_id = 4,
                    port =   1)#17
system.add_element(type = et.pir, 
                    name = 'Motion',
                    room_id = 3,
                    module_id = 1,
                    port =   3)#18

# id 4
system.add_element(type = et.ds, 
                    name = 'Temperature',
                    room_id = 4,
                    module_id = 4,
                    port =   1)#19
system.add_element(type = et.heater, 
                    name = 'Heater',
                    room_id = 4,
                    module_id = 2,
                    port =   4)#20
system.add_element(type = et.led, 
                    name = 'Led strip',
                    room_id = 4,
                    module_id = 3,
                    port =   2)#21
system.add_element(type = et.blind, 
                    name = 'Blind',
                    room_id = 4,
                    module_id = [2, 2],
                    port =   [5, 6])#22 23
system.add_element(type = et.switch,
                   name = 'Switch',
                   room_id = 4,
                   module_id = 1,
                   port = 12)#24
system.add_element(type = et.pir, 
                    name = 'Motion',
                    room_id = 4,
                    module_id = 1,
                    port =   4)#25
system.add_element(type = et.rs, 
                    name = 'RS window',
                    room_id = 4,
                    module_id = 1,
                    port =   5)#26

# id 5
system.add_element(type = et.ds, 
                    name = 'Temperature',
                    room_id = 5,
                    module_id = 4,
                    port =   1)#27
system.add_element(type = et.heater, 
                    name = 'Heater',
                    room_id = 5,
                    module_id = 2,
                    port =   7)#28
system.add_element(type = et.blind, 
                    name = 'Blind',
                    room_id = 5,
                    module_id = [2, 2],
                    port =   [8, 9])#29 30
system.add_element(type = et.switch,
                   name = 'Switch',
                   room_id = 5,
                   module_id = 1,
                   port = 13)#31
system.add_element(type = et.pir, 
                    name = 'Motion',
                    room_id = 5,
                    module_id = 1,
                    port =   6)#32
system.add_element(type = et.rs, 
                    name = 'RS window',
                    room_id = 5,
                    module_id = 1,
                    port =   7)#33

#id 6
system.add_element(type = et.ds, 
                    name = 'Temperature',
                    room_id = 6,
                    module_id = 4,
                    port =   1)#34
system.add_element(type = et.ls, 
                    name = 'Light level',
                    room_id = 6,
                    module_id = 4,
                    port =   2)#35
system.add_element(type = et.rs, 
                    name = 'RS Main doors',
                    room_id = 6,
                    module_id = 1,
                    port =   8)#36

#system.add_dependancy('wlaczanie swiatla w lazience', '[e3=1] then e2=100; e2=0{100};') #light tunr on for 100s after pir detection
system.add_regulation('Temp set', feed_el_id=5, out_el_id=6, set_point=20, dev=2) # room 1 heating
system.add_regulation('Temp set', feed_el_id=12, out_el_id=13, set_point=20, dev=2)# room 2 heating
system.add_regulation('Temp set', feed_el_id=19, out_el_id=20, set_point=20, dev=2)# room 4 heating
system.add_regulation('Temp set', feed_el_id=27, out_el_id=28, set_point=20, dev=2)#room 5 heating
system.add_dependancy('Turning off heater in parents sleeping room when window opened', '[e10=0] then e6=0;') #light tunr on for 100s after pir detection
system.add_dependancy('Turning off heater in living room when window opened', '[e26=0] then e20=0;') #light tunr on for 100s after pir detection
system.add_dependancy('Turning off heater in kitchen when window opened', '[e33=0] then e28=0;') #light tunr on for 100s after pir detection
system.add_dependancy('Turning off heater in kitchen when window opened', '[e33=0] then e28=0;') #light tunr on for 100s after pir detection
system.add_dependancy('Switching led in Johnys sleeping room', '[e15=1] then e14=100;') #light tunr on for 100s after pir detection

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

