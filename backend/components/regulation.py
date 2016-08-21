from backend.components.base_component import BaseComponent
from backend.components.element import OutputElement
from backend.misc.sys_types import Regt


class RegulationConfigError(Exception):
    def __init__(self, msg):
        self.msg = msg


class Regulation(BaseComponent):
    """Rehulation algoritms for controlling outputs based on inputs values"""
    
    table_name = "regulation"

    column_headers_and_types = BaseComponent.column_headers_and_types + [['feed_el_id', 'integer'],
                                                                         ['out_el_id', 'integer'],
                                                                         ['set_point', 'integer'],
                                                                         ['deviation', 'integer'], ]
                                                                        
    ID = 0

    ON = 1
    OFF = 0
     
    COL_FEED_EL_ID, COL_OUT_EL_ID, COL_SET_POINT, COL_DEVIATION = 3, 4, 5, 6
    items = {}

    def __init__(self, *args):

        super().__init__(args[0], Regt(args[1]), args[2])
        Regulation.items[self.id] = self
        self.feed_el_id = args[Regulation.COL_FEED_EL_ID]
        self.out_element = OutputElement.items[args[Regulation.COL_OUT_EL_ID]]
        self.set_point = args[Regulation.COL_SET_POINT]
        self.dev = args[Regulation.COL_DEVIATION]    # max alowable deviation from set point
        self.control = self.proportional_control  # Control algorithm

        self.priority = 10
        self.feed_val = None

    def notify(self, val):
        self.feed_val = val

    def run(self, ):
        """calculates whether output element should be on or off"""
        out_val = self.control()
        if out_val == Regulation.ON:
            self.out_element.desired_value = (out_val, self.priority, True)

        if out_val == Regulation.OFF:
            self.out_element.desired_value = (out_val, self.priority, False)

    def proportional_control(self, ):
        """If feed value is less than set value turn on regulation. Otherwise turn off"""
        if not self.feed_val: # if sensor does not returns any valu - its val == None
            return Regulation.OFF

        if self.feed_val < self.set_point:
            return Regulation.ON

        else:
            return Regulation.OFF

    def inverse_control(self, ):
        pass
