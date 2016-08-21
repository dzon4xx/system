import unittest

from backend.components.modbus_network import ModbusNetwork
from backend.components.module import AmbientBoard
from backend.components.module import InputBoard
from backend.components.module import LedLightBoard
from backend.components.module import OutputBoard
from backend.system_loader import objects_loader


class TestModbus(unittest.TestCase):

    def setUp(self):
        self.modbus = ModbusNetwork()
        self.modbus.open()

    def tearDown(self):
        self.modbus.close()
        del self.modbus

    def test_connection(self):
        self.assertTrue(self.modbus.connected)

    def test_baudrate_range(self):
        self.assertTrue(9600 <= self.modbus.baudrate <= 1000000)

    def test_t_3_5_range(self):
        self.assertTrue(1e-3 <= self.modbus.t_3_5 <= 1e-2)

    def test_reload(self):
        self.modbus.reload()

    def test_write_coils(self):
        self.assertTrue(self.modbus.write_coils(2, 0, [1 for _ in range(10)]), True)
        self.assertTrue(self.modbus.write_coils(2, 0, [0 for _ in range(10)]), True)

    def test_write_registers(self):
        self.assertTrue(self.modbus.write_regs(3, 0, [100 for _ in range(3)]), True)  # max power
        self.assertTrue(self.modbus.write_regs(3, 0, [0 for _ in range(3)]), True)  # min power

    def test_read_registers(self):
        self.assertTrue(self.modbus.read_regs(1, 0, 15), True)  # read all regs
