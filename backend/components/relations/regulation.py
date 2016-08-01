from backend.misc.sys_types import regt
from backend.components.base_object import Base_object
from backend.components.elements.element import Element, Input_element, Output_element

class Regulation_config_error(Exception):
    def __init__(self, msg):
        self.msg = msg


class Regulation(Base_object):
    """Algorytmy regulacyjne. Na wejsciu algorytm otrzymuje dane z wejscia. Na tej podstawie steruje wyjsciem zgodnie z podanym algorytmem"""
    
    table_name = "regulation"

    column_headers_and_types = Base_object.column_headers_and_types + [['feed_el_id', 'integer'], 
                                                                      ['out_el_id', 'integer'],
                                                                      ['set_point', 'integer'],
                                                                      ['deviation', 'integer'],]
                                                                        
    ID = 0
    items = {}

    ON = 1
    OFF = 0
    #regulation_fun_dict = {regt.direct  : Regulation.direct_control,
                           #regt.inverse : Regulation.inverse_control}
     
    COL_FEED_EL_ID, COL_OUT_EL_ID, COL_SET_POINT, COL_DEVIATION = 3, 4, 5, 6                       
    def __init__(self, *args):
        #self.__check_arguments(*args[Regulation.COL_FEED_EL_ID:])
        super().__init__(args[0], regt(args[1]), args[2]) # inicjalizuj id type, name
        Regulation.items[self.id] = self
        self.feed_el_id  = args[Regulation.COL_FEED_EL_ID]
        self.out_el_id = args[Regulation.COL_OUT_EL_ID]
        self.set_point  = args[Regulation.COL_SET_POINT]
        self.dev    = args[Regulation.COL_DEVIATION]    # deviation dopuszczalne odchylenie od nastawy
        self.control = self.proportional_control # For now only proportional control

        Element.items[self.feed_el_id].subscribe(self)

        self.priority = 10
        self.feed_val = None

    def __check_arguments(self, feed_el_id, out_el_id,  set_point, dev):
        """Sprawdza czy argumenty wejsciowe do regulatora maja sens. jesli nie to wywoluje Regulation_config_error"""
       
        #sprawdzanie nastaw temperatury
        #sprawdzanie wilgotnosci

    def run(self, ):
        """calculates whether output element should be on or off"""
        out_val =  self.control()
        if out_val == Regulation.ON:
            Output_element.items[self.out_el_id].desired_value = (out_val, self.priority, True)

        if out_val == Regulation.OFF:
            Output_element.items[self.out_el_id].desired_value = (out_val, self.priority, False)


    def proportional_control(self, ):

        if not self.feed_val: # if sensor does not returns any valu - its val == None
            return Regulation.OFF

        if self.feed_val < self.set_point:
            return Regulation.ON

        else:
            return Regulation.OFF

    def inverse_control(self, ):
        pass

    def notify(self, val):
        self.feed_val = val
