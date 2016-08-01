from server__client.server.models.user import User
from sys_database.database import create_db_object
import hashlib


db = create_db_object()

print("User name: ")
user_name = input()
user = db.read(User, 'name', user_name) # check user in db
if user: # if user exists
    print("User {} already registered".format(user_name))
else:
    print("Password: ")
    pwd = input()
    print("Repeat Password: ")
    rpt_pwd = input()
    if pwd != rpt_pwd:
        print("Passwords does not match")
    else:
        hash_pwd = hashlib.md5(pwd.encode('utf-8'))
        db.save(User, (None, user_name, hash_pwd.hexdigest(), 0)) # 0 means user not logged in