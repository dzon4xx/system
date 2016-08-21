import logging
import json
import tornado.web
from ..models.user import User
from backend.sys_database.database import create_db_object

paths = (r'auth/login_page.html',)

actions = ['login', 'logout']   #nie zmieniac kolejnosci. mozna nazwe

class AuthenticationHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        self.db = create_db_object()
        self.logger = logging.getLogger('AUTH')
        self.logger.disabled = False
        self.logger.setLevel(logging.INFO)
        return super().__init__(application, request, **kwargs)

    def login(self, data):
        
        db_user = self.db.read(User, 'name', data['name'])
        
        if db_user:
            if db_user.loged_in:
                self.write("ok")
                self.logger.info("LOGGED IN: " + str(db_user))                 
                return True 

            elif data['password'] == db_user.password:
                db_user.loged_in = True;
                self.db.update_field(db_user, 'logged_in', 1)
                self.write("ok") 
                self.logger.info("LOGGED IN: " + str(db_user))                 
                return True
                            
            else:
                self.logger.info("WRONG PASSWORD: " + str(db_user)) 
                self.write("error");
                return False
        else:
            self.logger.info("NOT IN DATABASE: " + str(db_user))
            self.write("error")
            return False

    def logout(self, data):
        self.db = create_db_object()
        db_user = self.db.read(User, 'name', data['name'])
        if db_user:
            if db_user.loged_in == True:
                db_user.loged_in = False
                self.db.update_field(db_user, 'logged_in', 0)
                self.write("ok")
                self.logger.info("LOGGED OUT: " + str(db_user)) 
                              
            else:
                self.write("error")
                self.logger.warning("USER: " + str(db_user) + " was logged out and attempted to log out once again")   

        else:
            self.write("error")
            self.logger.warning("USER: " + str(db_user) + " not recognized while logging out")

    def get(self):
        self.render('login_page.html')
                
    def validate_in_data(self, in_data):
        
        #sprawdz czy uzytkownik wyslal poprawna akcje
        in_action = in_data['action']
        try:
            assert (in_action in actions)
            
        except AssertionError as e:
            self.logger.warn(in_action + " is not valid action!")
            return False
                      
        return True;

    def post(self):
        actions_map = {actions[0] : self.login, actions[1] : self.logout}
        in_data = json.loads(self.request.body.decode('UTF-8'))

        if self.validate_in_data(in_data):
            action = in_data['action']     
            actions_map[action](in_data)
        else:
            self.write("error")






