#!/usr/bin/python
from os import path
import tornado
from tornado.log import access_log

from server.handlers.init_handler import InitHandler
from server.handlers.auth_handler import AuthenticationHandler
from server.handlers.ui_handler import UiHandler
from server.handlers.websocket import Websocket
from server import port
from server.models.system_representation import load_system_representation

from backend.misc.color_logs import color_logs

def load_routers():

    routers = [(r"/", InitHandler)]

    routers.append((r"/auth.*", AuthenticationHandler))
    routers.append((r"/ui.*", UiHandler))
    routers.append((r"/websocket", Websocket))

    return routers

def load_app(port, root):
    settings = {
        "socket_io_port": port,
        "static_path": path.join(root, "client"),
        "template_path": path.join(root, "client"),
        "debug" : True,
        "xsrf_cookies": False,
    }
    
    routers = load_routers()

    application = tornado.web.Application(
        routers,
        **settings
    )
    access_log.info("Starting server")
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()



if __name__ == "__main__":

    access_log.disabled = True #Tornado access log

    color_logs()
    root = path.dirname(__file__)
    load_system_representation()
    load_app(port, root)
    



