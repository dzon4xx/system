class User():
       
    table_name = "users"
    column_headers_and_types = [['id', 'integer primary key'], 
                                ['name', 'text'], 
                                ['password', 'text'], 
                                ['logged_in', 'integer'],]

    COL_PASS  = 3
    COL_LOGGED_IN = 4

    def __init__(self, *args):
        self.id, self.user_name, self.password, self.loged_in = args 

    def __str__(self,):
        return "user name: " + self.user_name + " password: " + self.password

  


