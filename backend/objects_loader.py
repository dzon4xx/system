from backend.sys_database.database import Database, create_db_object
from backend.components.modules.module import Anfa_output, Anfa_led_light, Anfa_ambient, Anfa_input
from backend.components.elements.element import Output_element, Input_element, Blind
from backend.components.relations.dependancy import Dependancy
from backend.components.relations.regulation import Regulation

def objects_loader():

    db = create_db_object()

    db.load_objects_from_table(Input_element)
    db.load_objects_from_table(Output_element)
    db.load_objects_from_table(Blind)
    
    db.load_objects_from_table(Dependancy)
    db.load_objects_from_table(Regulation)
    
    db.load_objects_from_table(Anfa_output)
    db.load_objects_from_table(Anfa_led_light)
    db.load_objects_from_table(Anfa_ambient)
    db.load_objects_from_table(Anfa_input)