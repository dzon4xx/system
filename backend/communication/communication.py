import websocket
import threading
import logging
import os
import time
class Communication_manager(threading.Thread):
    
    url = "ws://localhost:8888/websocket"

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name='COM')
        self.logger = logging.getLogger('COM')
        self.in_buffer = []
        self.out_buffer = []
        

        #self.conn = websocket.create_connection(Communication_manager.url, header = {'name' :'logic'})



    def run(self, ):
        self.logger.info("Start")
        try:
            while True:
                time.sleep(0.01)
                #msg = self.conn.recv()
                #self.logger.debug(msg)
                #if msg is not None:
                #    self.out_buffer.append(msg)

                #if self.in_buffer:
                #    for msg in self.in_buffer:
                #        self.conn.send(msg)

                #    self.in_buffer = []
        except websocket.WebSocketConnectionClosedException:
            self.logger.error("Websocet disconnected")
            os._exit(1)





    
