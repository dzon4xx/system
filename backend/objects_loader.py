from backend.sys_database.database import Database, create_db_object
from backend.components.modules.module import Output_board, Led_light_board, Ambient_board, Input_board
from backend.components.elements.element import Output_element, Input_element, Blind
from backend.components.relations.dependancy import Dependancy
from backend.components.relations.regulation import Regulation

def objects_loader():
    """Loads all necessary objects for system operation from database"""

    db = create_db_object()

    db.load_objects_from_table(Input_element)
    db.load_objects_from_table(Output_element)
    db.load_objects_from_table(Blind)
    
    db.load_objects_from_table(Dependancy)
    db.load_objects_from_table(Regulation)
    
    db.load_objects_from_table(Output_board)
    db.load_objects_from_table(Led_light_board)
    db.load_objects_from_table(Ambient_board)
    db.load_objects_from_table(Input_board)