from enum import Enum


class BaseComponent(object):
    """Base component for all system components It stores id type name and trivial string representation"""
    column_headers_and_types = [['id', 'integer primary key'],
                                ['type', 'integer'],
                                ['name', 'text'], ]
    COL_ID, COL_TYPE, COL_NAME = 0, 1, 2  # numery kolumn

    def __init__(self, *args):
        self.id, self.type, self.name = args

        #if not isinstance(self.id, int):
        #   raise TypeError("Id must be int")

        if not (isinstance(self.type, int) or isinstance(self.type, Enum)):
            raise TypeError("Type must be int or enum")

        if not isinstance(self.name, str):
            raise TypeError("name must be str")

        #if self.id < 0:
        #    raise ValueError("Component id must be positive number")

    def __str__(self, ):
        """Representation of object"""
        return "".join(["ID: ", str(self.id), "\ttype: ", self.type.name, "\tname: ", self.name])

    def __repr__(self,):
        return "".join(["ID: ", str(self.id), " type: ", self.type.name])





