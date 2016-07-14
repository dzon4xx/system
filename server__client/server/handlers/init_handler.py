import tornado.web
import json
class InitHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("init/init.html")            