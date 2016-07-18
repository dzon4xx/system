from common.sys_types import regt
from common.base_object import Base_object
from common.elements.element import Element
from common.elements.input_element import Input_element
from common.elements.output_element import Output_element

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

    #regulation_fun_dict = {regt.direct  : Regulation.direct_control,
                           #regt.inverse : Regulation.inverse_control}
     
    COL_FEED_EL_ID, COL_OUT_EL_ID, COL_SET_POINT, COL_DEVIATION = 3, 4, 5, 6                       
    def __init__(self, *args):
        self.__check_arguments(*args[Regulation.COL_FEED_EL_ID:])
        super().__init__(args[0], regt(args[1]), args[2]) # inicjalizuj id type, name
        Regulation.items[self.id] = self
        self.out_el_id  = args[Regulation.COL_FEED_EL_ID]
        self.feed_el_id = args[Regulation.COL_OUT_EL_ID]
        self.set_point  = args[Regulation.COL_SET_POINT]
        self.dev    = args[Regulation.COL_DEVIATION]    # deviation dopuszczalne odchylenie od nastawy
        #self.control = Regulation[self.type]

        Element.items[self.feed_el_id].subscribe(self)

        self.feed_val = None

    def __check_arguments(self, out_el_id, feed_el_id, set_point, dev):
        """Sprawdza czy argumenty wejsciowe do regulatora maja sens. jesli nie to wywoluje Regulation_config_error"""
        if out_el_id not in Output_element.items.keys():
            raise Regulation_config_error('Output element: ' + str(out_el_id) + " not in defined output elements")
        if feed_el_id not in Input_element.items.keys():
            raise Regulation_config_error('Feed element: ' + (out_el_id) + " not in defined input elements")

        #sprawdzanie nastaw temperatury
        #sprawdzanie wilgotnosci

    def run(self, ):
        
        out_val =  self.control(feed_val, self.hist)
        self.out_el.set_desired_value(self, out_val)

    def direct_control(self, feed_val, hist):
        pass

    def inverse_control(self, ):
        pass

    def notify(self, val):
        self.feed_val = val

