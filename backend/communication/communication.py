import websocket
import threading
import logging

class Communication():
    
    url = "ws://localhost:8888/websocket"

    def __init__(self, ):
        self.logger = logging.getLogger('COM')
        self.logger.disabled = False
        self.logger.setLevel("DEBUG")
        self.in_buffer = []
        self.out_buffer = []
        
        self.conn = websocket.create_connection(Communication.url, header = {'name' :'logic'})


    def run(self, ):
        
        while True:
            msg = self.conn.recv()
            print(msg)
            if msg is not None:
                self.out_buffer.append(msg)

            if self.in_buffer:
                for msg in self.in_buffer:
                    self.conn.send(msg)

                self.in_buffer = []



if __name__ == "__main__":

    com = Communication()
    com.run()
    
