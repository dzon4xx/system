from common.sys_types import et, mt
from common.elements.input_element import Input_element
from common.elements.output_element import Efect_cause_element, Regulated_element
from common.module import Ambient_module, Output_module, Input_module

in_el = Input_element(et.ls, 'ds w kuchni', [1, 2, 3, 4])
in_el1 = Input_element(et.ds, 'ds w kuchni', [1, 2, 3, 4])
ec_el = Efect_cause_element(et.blind, 'roleta w kuchni', 1 ,5, 'causes', 'efects')
reg_el = Regulated_element(et.heater, 'grzenik w salonie', 2 , 3, 3, 50)


ambient = Ambient_module(mt.ambient, 'Stacja pogodowa')
input = Input_module(mt.input, 'Modul wejsciowy')
output = Output_module(mt.output, 'Modul wyjsciowy')
led = Output_module(mt.led_light, 'Modul led')

try:
    ambient.add_element(1, in_el1)
    #ambient.add_element(1, in_el)
    #output.add_element(ec_el.port, ec_el)
    output.add_element(reg_el.port, reg_el)

except Exception as e:
    print (e.msg)

print (str(output))



#print (str(ec_el))
#print (str(reg_el))
#print (Efect_cause_element.column_headers_and_types)
#print (Regulated_element.column_headers_and_types)
#print (str(in_el))


def parse_condition(condition):
    """Parsuje string warunku i tworzy obiekt warunku czasowego lub zwyklego"""

    operator_pos = 0
    operator = None
    for s_pos, s in enumerate(condition):
        if s in ('=', '<', '>'):
            operator_pos = s_pos
            operator = s
            break

    element = condition[:operator_pos]
    comp_value = condition[operator_pos+1:]

    print (element, comp_value, operator)

import time

start_time = time.time()
start_clock= time.clock()

time.sleep(1)

print ( (time.time()- start_time)*1000)
print( (time.clock()-start_clock) *1000)


import dominate
from dominate.tags import *

doc = dominate.document(title='Dominate your HTML')

with doc.head:
    link(rel='stylesheet', href='style.css')
    script(type='text/javascript', src='script.js')

with doc:
    with div(id='header').add(ol()):
        for i in ['home', 'about', 'contact']:
            li(a(i.title(), href='/%s.html' % i))

    with div():
        attr(cls='body')
        p('Lorem ipsum..')

print(doc)


room_container = div(cls = "container")
room_container.add(br(), br(), h1('test'))

print (room_container)





