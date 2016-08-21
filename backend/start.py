import threading
import time

from backend.managers.communication import CommunicationManager
from backend.managers.logic import LogicManager
from backend.managers.modbus import ModbusManager
from backend.misc.color_logs import color_logs
from backend.system_loader import system_loader

#zabezpieczyc bufory przed kolizja watkow. Tzn logika usuwa bufor a w tym samym czasie komunikacja pisze do buforu

time.sleep(1)

color_logs()

system = system_loader()

communication = CommunicationManager()
logic = LogicManager(args=(communication.out_buffer, communication.in_buffer, system))
modbus_manager = ModbusManager(args=(logic.tasks, system.modules.input))

communication.logger.disabled = False
communication.logger.setLevel("ERROR")

modbus_manager.logger.disabled = False
modbus_manager.logger.setLevel("ERROR")#DEBUG

modbus_manager.modbus.logger.disabled = False
modbus_manager.modbus.logger.setLevel("ERROR")

logic.logger.disabled = False
logic.logger.setLevel("DEBUG")

communication.setDaemon(True)
logic.setDaemon(True)
modbus_manager.setDaemon(True)

communication.start()
logic.start()
modbus_manager.start()

while threading.active_count() > 0:
    time.sleep(2)

