import logging
import threading
import time

from backend.components.modbus_network import ModbusNetwork


class ModbusManager(threading.Thread):

    def __init__(self, args=()):
        threading.Thread.__init__(self, group=None, target=None, name='MODBUS')
                 
        self.logger = logging.getLogger('MODBUS_MAN')
        self.modbus = ModbusNetwork()
        self._open_modbus()  # loop while modbus is not opened

        self.tasks = args[0]
        self.input_modules = args[1]

    def _open_modbus(self):
        while not self.modbus.connected:
            if not self.modbus.open():
                self.logger.error('Modbus connection error. Retrying connection'.format(self.name))
                time.sleep(10)
            time.sleep(0.5)  # sleep to allow slaves to configure themselfs

    def _write_pending_modules(self, ):

        while not self.tasks.empty():
            output_module = self.tasks.get()  # get output element form task queue
            if output_module.is_available():
                result = output_module.write()
                if result is False:
                    output_module.available = False

    def run(self, ):
            self.logger.info('Thread {} start'. format(self.name))

            while True:
                for input_module in self.input_modules.values():  # loop for every input module to get high response speed
                    self._write_pending_modules()  # after every read of in_mod check if there is anything to write to out_mod

                    if input_module.is_available():
                        input_module.read()  # reads values and sets them to elements

                    if not self.modbus.is_available():
                        self.modbus.reload()

                #    self.modbus.debug()
