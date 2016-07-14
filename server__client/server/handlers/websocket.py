import logging
from tornado.websocket import  WebSocketHandler
from server__client.server.models.visual_element import Visual_element

socket_logger = logging.getLogger('WS')
socket_logger.disabled = False
socket_logger.setLevel("DEBUG")

class Websocket(WebSocketHandler):

    clients = set()
    logic = None

    def open(self, ):
      
        if 'Name' in self.request.headers._dict:
            self.name = self.request.headers._dict['Name']
            Websocket.logic = self
            socket_logger.info("logic connected")
        else:
            self.name = self.get_cookie('name')
            Websocket.clients.add(self)
            socket_logger.info("client connected")


    def on_message(self, message):
        socket_logger.debug(self.name, 'send: ', message)
        if self == Websocket.logic:
            data = message.split(',')
            Visual_element.items[int(data[0][1:])].value = data[1]
            for con in Websocket.clients:
                con.write_message(message)
        else:
            socket_logger.debug(message)
            Websocket.logic.write_message(message)

    def on_close(self):
        if self != Websocket.logic:        
            Websocket.clients.remove(self)

    def check_origin(self, origin):
        return True