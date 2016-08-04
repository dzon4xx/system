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
        self.in_buffer = queue.Queue(100)
        self.out_buffer = queue.Queue(100)

        self.msg = None # msg from websocet

        self.connected = False
        while not self.connected:
            try:
                self.conn = websocket.create_connection(Communication_manager.url, header = {'secret' :'f59c8e3cc40bdc367d81f0c6a84b1766'})
                self.connected = True
            except:
                self.logger.error("Can't connect to server")
                time.sleep(0.2)
                

        wst = threading.Thread(target = self.listen_ws)
        wst.setDaemon(True)
        wst.start()

    def run(self, ):
        self.logger.info('Thread {} start'. format(self.name))
        if self.connected:
            try:
                while True:
                    time.sleep(0.1)
                    #self.debug()
                    while not self.in_buffer.empty():
                        msg = self.in_buffer.get()
                        self.conn.send(msg)
                    
            except websocket.WebSocketConnectionClosedException:
                self.logger.error("Websocket disconnected")
                os._exit(1)
            
    def listen_ws(self, ):
        while True:
            self.msg = self.conn.recv()
            self.out_buffer.put(self.msg)
            self.logger.debug(self.msg)

if __name__ == "__main__":
    from timeit import default_timer as t
    from backend.misc.color_logs import color_logs

    color_logs()
    communication = Communication_manager()
    communication.logger.disabled = False
    communication.logger.setLevel("DEBUG")

    while True:
        communication.run()

    
