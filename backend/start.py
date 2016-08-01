import time
import threading
import logging
from backend.misc.check_host import is_RPI
#import ptvsd
#tcp://backend@localhost:8082
#ptvsd.enable_attach(secret="backend", address = ('127.0.0.1', 8082))

from backend.communication.communication import Communication_manager
from backend.logic.logic import Logic_manager
from backend.modbus.modbus_manager import Modbus_manager
from backend.objects_loader import objects_loader
from backend.misc.color_logs import color_logs

#zabezpieczyc bufory przed kolizja watkow. Tzn logika usuwa bufor a w tym samym czasie komunikacja pisze do buforu
if is_RPI:
    time.sleep(1)
import queue
color_logs()

objects_loader()

communication = Communication_manager()
logic = Logic_manager(args=(communication.out_buffer, communication.in_buffer,))
modbus_manager = Modbus_manager(args=(logic.tasks,))


communication.logger.disabled = False
communication.logger.setLevel("INFO")

modbus_manager.logger.disabled = False
modbus_manager.logger.setLevel("INFO")

modbus_manager.modbus.logger.disabled = False
modbus_manager.modbus.logger.setLevel("INFO")

logic.logger.disabled = False
logic.logger.setLevel("INFO")

communication.setDaemon(True)
logic.setDaemon(True)
modbus_manager.setDaemon(True)

communication.start()
logic.start()
modbus_manager.start()

while threading.active_count() > 0:
    time.sleep(2)

