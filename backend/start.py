import threading
from backend.communication.communication import Communication
from backend.logic.logic import Logic
from backend.modbus.modbus import Modbus
from common.color_logs import color_logs

#zabezpieczyc bufory przed kolizja watkow. Tzn logika usuwa bufor a w tym samym czasie komunikacja pisze do buforu
color_logs()
communication = Communication()
modbus = Modbus()
logic = Logic(args=(communication,))


communication.logger.disabled = False
communication.logger.setLevel("DEBUG")

modbus.logger.disabled = False
modbus.logger.setLevel("DEBUG")

logic.logger.disabled = False
logic.logger.setLevel("DEBUG")


communication.start()
logic.start()

