#!/usr/bin/python
from os import path
import tornado
from server.handlers.init_handler import InitHandler
from server.handlers.auth_handler import AuthenticationHandler
from server.handlers.ui_handler import UiHandler
from server.handlers.websocket import Websocket
from tornado.log import access_log
from server import port
from server.models.system_representation import load_system_representation

from common.color_logs import color_logs

access_log.disabled = False


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
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()



if __name__ == "__main__":

    color_logs()
    root = path.dirname(__file__)
    print ("start")
    load_system_representation()
    load_app(port, root)
    



