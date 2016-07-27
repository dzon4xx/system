import websocket
import threading
import logging
import os
import time
import queue
class Communication_manager(threading.Thread):
    
    url = "ws://localhost:8888/websocket"

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name='COM')
        self.logger = logging.getLogger('COM')
        self.in_buffer = set()
        self.out_buffer = set()

        self.msg = None # msg from websocet

        self.connected = False
        try:
            self.conn = websocket.create_connection(Communication_manager.url, header = {'secret' :'f59c8e3cc40bdc367d81f0c6a84b1766'})
            self.connected = True
        except:
            self.logger.error("Can't connect to server")
            return


        wst = threading.Thread(target = self.listen_ws)
        wst.setDaemon(True)
        wst.start()


    def run(self, ):
        self.logger.info('Thread {} start'. format(self.name))
        if self.connected:
            try:
                while True:
                    time.sleep(0.1)
                    if self.in_buffer:
                        while self.in_buffer:
                            msg = self.in_buffer.pop()
                            self.conn.send(msg)
            
            except websocket.WebSocketConnectionClosedException:
                self.logger.error("Websocet disconnected")
                os._exit(1)


    def listen_ws(self, ):
        while True:
            self.msg = self.conn.recv()
            self.out_buffer.add(self.msg)
            #self.logger.debug(self.msg)





    
