import logging
from tornado.websocket import  WebSocketHandler
from server_client.server.models.visual_element import Visual_element

socket_logger = logging.getLogger('WS')
socket_logger.disabled = False
socket_logger.setLevel("INFO")


class Websocket(WebSocketHandler):

    clients = set()
    logic = None

    def open(self, ):
        """Opens websocet connection """
        if 'Secret' in self.request.headers._dict:
            secret = self.request.headers._dict['Secret']
            if secret == 'f59c8e3cc40bdc367d81f0c6a84b1766': # if logic password matches
                Websocket.logic = self
                self.name = 'logic'
                socket_logger.info("logic connected")
            else:
                socket_logger.warn("Attempted unauthorized logic connection")
                self.close()
        else:
            self.name = self.get_cookie('name')
            Websocket.clients.add(self)
            socket_logger.info("client: {} connected".format(self.name))

    def on_message(self, message):
        socket_logger.debug('%s send: %s',self.name, message)

        if self == Websocket.logic: 
            data = message.split(',')
            id = data[0]
            value = data[1]
            Visual_element.items[id].value = value # Save of actual values in server memory
            for con in Websocket.clients: # pass message to all clients
                socket_logger.debug('passing to clients')
                con.write_message(message)
        else:
            if Websocket.logic: 
                socket_logger.debug('sending to logic')
                Websocket.logic.write_message(message)# pass message to logic

    def on_close(self):
        if self != Websocket.logic:        
            socket_logger.info("client: {} disconnected".format(self.name))
            Websocket.clients.remove(self)
        if self == Websocket.logic:
            socket_logger.info("logic disconected")
            Websocket.logic = None

    def check_origin(self, origin):
        return True