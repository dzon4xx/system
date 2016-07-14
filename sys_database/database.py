"""Database handling class"""

import sys
import sqlite3 as sql
import logging
from functools import wraps


def create_db_object(is_log_disabled = True):
    root = sys.path[-1]
    db_path =  "\\".join([root, 'sys_database', "sys_database.db"])

    db_logger = logging.getLogger('DB')
    db_logger.disabled = is_log_disabled
    db_logger.setLevel(logging.DEBUG)

    return Database(db_path, db_logger)

def save_create(func):
    """Handles connection commit eventual rollback and closing while saving or creating to database"""
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if args[0].connect():
            try:
                args[0].cur = args[0].con.cursor()            
                return func(*args, **kwargs)               
            except sql.Error as e:
                args[0].con.rollback()               
                args[0].logger.exception( "DATABASE SAVE/CREATE Error %s:",  e.args[0])
                pass
            finally:
                args[0].con.commit() 
                args[0].close()
        else:
            pass
    return func_wrapper

def read_remove(func):
    """Handles connection and closing of database while reading or removing from database"""
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if args[0].connect():
            try:
                args[0].cur = args[0].con.cursor()
                return func(*args, **kwargs)
            except sql.Error as e:               
                args[0].logger.exception( "DATABASE READ/REMOVE Error %s:", e.args[0])

            finally:
                args[0].close()
        else:
            args[0].logger.warning("Cannot open database")
            return 0
    return func_wrapper

class Database:
    """ Handles system database """
    def __init__(self, path, logger):
        self.path = path
        self.logger = logger
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

    def connect(self):
        """Connects to database. If database does not exist creates one"""
        try:
            
            self.con = sql.connect(self.path)
            self.__connected = True
            self.logger.debug("Database opened")
        except sql.Error as e:
            self.__connected = False
            self.logger.warning(e.args[0])
        finally:
            return self.__connected
                     
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
            #sprawdzenie czy tablica istnieje
            self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='" + Object.table_name +"'")
            tables = self.cur.fetchall()
            if not tables :
                #Przygotowanie komendy sql
                column_headers_and_types = [ ' '.join(col_header_and_type) for col_header_and_type in Object.column_headers_and_types]
                column_headers_and_types_str = self._brackets(','.join(column_headers_and_types))
                sql_command = self._put_spaces(self.sql_CREATE_TABLE, Object.table_name, column_headers_and_types_str)

                self.cur.execute(sql_command);
                self.logger.info("table: " + Object.table_name + " created")

    @read_remove
    def get_table(self, Object):
        sql_command = self._put_spaces(self.sql_SELECT, '*', self.sql_FROM, Object.table_name)
        self.cur.execute(sql_command)
        return self.cur.fetchall()

    @read_remove
    def remove_table(self, Object):
        """Removes table from database"""
        self.cur.execute("DROP TABLE " + Object.table_name)
        self.logger.info("Table: " + Object.table_name + " droped")

    @save_create
    def save(self, Object, db_values):
        """Saves user to database"""
       
        #Przygotowanie naglowkow kolumn i ich typow
        column_headers = [ col_head_and_type[0] for col_head_and_type in Object.column_headers_and_types]
        column_headers_str = self._brackets (",".join(column_headers) )
        
        #Przygotowanie znakow zapytania w ilosci odpowiadajacej ilosci kolumn
        question_marks = ""
        for col_head in Object.column_headers_and_types:
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
        object_data = list(self.cur.fetchone())
        if not object_data:
            return False
        return Object(*object_data)
    
    @save_create
    #def update_user_log_status(self, user):
    def update_field(self, object, field_name,  field_value):
        sql_command = self._put_spaces(self.sql_UPDATE, object.table_name, self.sql_SET, field_name, '=?', self.sql_WHERE, "id=?")
        self.cur.execute(sql_command, (field_value, object.id))
        #self.cur.execute("UPDATE users SET logged_in=?"  " WHERE user_name=?",(str(int(user.loged_in)), user.user_name,))
         

    def _brackets(self, str):
        return '(' + str + ')'

    def _put_spaces(self, *args):
        str = ""
        for arg in args:
            str += arg + " "

        return str.rstrip(" ")