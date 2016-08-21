"""Database handling class"""

import sys
import sqlite3 as sql
import logging
from functools import wraps

from backend.misc.check_host import is_RPI


def create_db_object():

    root = None
    for path in sys.path:
        if path.endswith("system"):
            root = path

    if is_RPI:
        db_path = "/".join([root, 'backend', 'sys_database', "sys_database.db"])
    else:   
        db_path = "\\".join([root, 'backend', 'sys_database', "sys_database.db"])

    return Database(db_path)


def save_create(func):
    """Handles connection commit eventual rollback and closing while saving or creating to database"""
    @wraps(func)
    def func_wrapper(self, *args):
        if self.connect():
            try:
                self.cur = self.con.cursor()
                return func(self, *args)
            except sql.Error as e:
                self.con.rollback()
                self.logger.exception("DATABASE SAVE/CREATE Error %s:",  e.args[0])
                pass
            finally:
                self.con.commit()
                self.close()
        else:
            pass
    return func_wrapper


def read_remove(func):
    """Handles connection and closing of database while reading or removing from database"""
    @wraps(func)
    def func_wrapper(self, *args):
        if self.connect():
            try:
                self.cur = self.con.cursor()
                return func(self, *args)
            except sql.Error as e:               
                self.logger.exception("DATABASE READ/REMOVE Error %s:", e.args[0])

            finally:
                self.close()
        else:
            self.logger.warning("Cannot open database")
            return 0
    return func_wrapper


class Database:
    """ Handles system database """
    def __init__(self, path):
        self.path = path
        self.logger = logging.getLogger('DB')
        self.logger.disabled = False
        self.logger.setLevel(logging.ERROR)

        self.con = None
        self.cur = None
        self.__connected = False
        
        self.table_headers = {}

        self.sql_INSERT_INTO = "INSERT INTO"
        self.sql_VALUES = "VALUES"
        self.sql_CREATE_TABLE = "CREATE TABLE"
        self.sql_SELECT = "SELECT"
        self.sql_FROM = "FROM"
        self.sql_WHERE = "WHERE"
        self.sql_UPDATE = "UPDATE"
        self.sql_SET = "SET"
        self.sql_DELETE = "DELETE"

    def connect(self):
        """Connects to database. If database does not exist creates one"""
        self.con = sql.connect(self.path)
        self.__connected = True
        self.logger.debug("Database opened")
        return True
                     
    def close(self):
        """Closes connection to database"""
        if self.__connected:
            self.con.close()
            self.__connected = False
            self.logger.debug("Database closed")
        else:
            pass

    @save_create
    def create_tables(self, *Objects):
        """For every Object in Objects if Object's table does not exists creates one """

        for Object in Objects:
            # Check if the table exists
            self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='" + Object.table_name +"'")
            tables = self.cur.fetchall()
            if not tables:
                # Prepare sql command
                column_headers_and_types = [' '.join(col_header_and_type) for col_header_and_type in Object.column_headers_and_types]
                column_headers_and_types_str = self._brackets(','.join(column_headers_and_types))
                sql_command = self._put_spaces(self.sql_CREATE_TABLE, Object.table_name, column_headers_and_types_str)

                self.cur.execute(sql_command)
                self.logger.info("table: " + Object.table_name + " created")

    @read_remove
    def get_table(self, Object):
        sql_command = self._put_spaces(self.sql_SELECT, '*', self.sql_FROM, Object.table_name)
        self.cur.execute(sql_command)
        return self.cur.fetchall()

    @read_remove
    def clear_table(self, Object):
        sql_command = self._put_spaces(self.sql_DELETE, self.sql_FROM, Object.table_name)
        self.cur.execute(sql_command)

    def load_objects_from_table(self, Object):
        """Functions allows to retrieve objects from table based on object type"""
        table = self.get_table(Object)

        try:
            types = Object.types.copy()
            num_types = set()

            while types:
                num_types.add(types.pop().value)  # convert enums to ints

            for data in table:
                if data[1] in num_types:  # if type of object match with requierd type
                    data = list(data)
                    Object(*data)   # create Object
        except AttributeError: 
            for data in table: # simple load for objects without type
                data = list(data)
                Object(*data)   # create Object

    @read_remove
    def delete_tables(self, *Objects):
        """Removes tables from database"""
        for Object in Objects:
            self.cur.execute("DROP TABLE " + Object.table_name)
            self.logger.info("Table: " + Object.table_name + " droped")

    @save_create
    def save(self, Object, db_values):
        """Saves user to database"""
       
        # Prepare column headers
        column_headers = [ col_head_and_type[0] for col_head_and_type in Object.column_headers_and_types]
        column_headers_str = self._brackets (",".join(column_headers) )
        
        # Przygotowanie question marks for sql query
        question_marks = ""
        for _ in Object.column_headers_and_types:
            question_marks += '?,'   
        question_marks = self._brackets(question_marks.rstrip(','))

        sql_command = self._put_spaces(self.sql_INSERT_INTO, Object.table_name, column_headers_str, self.sql_VALUES, question_marks)
        self.cur.execute(sql_command, db_values)

        self.logger.info(str(Object) + " added to DB")

    @read_remove
    def read(self, Object, key_name, key):
        """Reads object based on given key from database"""
        sql_command = self._put_spaces(self.sql_SELECT, "*", self.sql_FROM, Object.table_name, self.sql_WHERE, key_name, '=', '?')
        self.cur.execute(sql_command, (key,))
        object_data = self.cur.fetchone()
        if not object_data:
            return False
        return Object(*list(object_data))

    @read_remove
    def read_simple(self, table_name, key_name, key):
        """Reads object based on given key from database"""
        sql_command = self._put_spaces(self.sql_SELECT, "*", self.sql_FROM, table_name, self.sql_WHERE, key_name, '=', '?')
        self.cur.execute(sql_command, (key,))
        object_data = list(self.cur.fetchone())
        if not object_data:
            return False
        return object_data
    
    @save_create
    # def update_user_log_status(self, user):
    def update_field(self, object, field_name,  field_value):
        sql_command = self._put_spaces(self.sql_UPDATE, object.table_name, self.sql_SET, field_name, '=?', self.sql_WHERE, "id=?")
        self.cur.execute(sql_command, (field_value, object.id))
         
    def _brackets(self, str):
        return '(' + str + ')'

    def _put_spaces(self, *args):
        str = ""
        for arg in args:
            str += arg + " "

        return str.rstrip(" ")