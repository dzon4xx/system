from collections import namedtuple

from backend.components.clock import Clock
from backend.components.element import OutputElement
from backend.components.element import InputElement
from backend.components.element import Blind
from backend.components.element import Element

from backend.components.module import Module
from backend.components.module import InputModule
from backend.components.module import OutputModule
from backend.components.module import OutputBoard
from backend.components.module import LedLightBoard
from backend.components.module import AmbientBoard
from backend.components.module import InputBoard

from backend.components.dependancy import Dependancy
from backend.components.regulation import Regulation

from backend.sys_database.database import create_db_object


def system_loader():
    """Loads all necessary objects for system operation from database
    Configures system and returns system named tuple"""

    system = namedtuple("System",
                        ["clock",
                         "elements",
                         "modules",
                         "dependancies",
                         "regulations"])

    system.elements = namedtuple("elements", ['all', 'input', 'output'])
    system.modules = namedtuple("modules", ['all', 'input', 'output'])
    system.modules.input = namedtuple("input_modules", ['input_board', 'ambient_board'])
    system.modules.output = namedtuple("input_modules", ['output_board', 'led_light_board'])

    system.clock = Clock()  # instantiate global clock. Reference is stored in clock.py

    db = create_db_object()
    db.load_objects_from_table(InputElement)
    db.load_objects_from_table(OutputElement)
    db.load_objects_from_table(Blind)

    db.load_objects_from_table(OutputBoard)
    db.load_objects_from_table(LedLightBoard)
    db.load_objects_from_table(AmbientBoard)
    db.load_objects_from_table(InputBoard)

    db.load_objects_from_table(Dependancy)
    db.load_objects_from_table(Regulation)

    for element in Element.items.values():
        module = Module.items[element.module_id]
        module.elements[element.reg_id] = element  # pass elements to modules registers

    # pair blinds so two motors of the same blinds never turn on both. It would cause shortcut!
    for blind in Blind.items.values():
        other_blind_id = blind.other_blind
        blind.other_blind = Blind.items[other_blind_id]

    for dep in Dependancy.items.values():
        dep._parse_cause(all_elements=Element.items)

    for reg in Regulation.items.values():
        InputElement.items[reg.feed_el_id].subscribe(reg)

    system.elements.all = Element.items
    system.elements.input = InputElement.items
    system.elements.output = OutputElement.items
    system.modules.input = InputModule.items
    system.modules.output = OutputModule.items
    system.dependancies = Dependancy.items
    system.regulations = Regulation.items

    return system




