import tornado.web
class InitHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("init.html")            