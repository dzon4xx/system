import unittest

from backend.components.module import Module
from backend.components.module import OutputModule
from backend.components.module import InputModule
from backend.components.module import OutputBoard
from backend.components.module import InputBoard
from backend.components.module import LedLightBoard
from backend.components.module import AmbientBoard


class TestModule(unittest.TestCase):

    def setUp(self):
        _id, _type, name = (0, 1, '')

        self.module = Module(_id, _type, name)

    def test_is_available_when_available(self):
        # when
        self.module.available = True

        # then
        self.assertTrue(self.module.is_available())

    def test_is_available_when_not_available(self):
        # when
        self.module.available = False

        # then
        self.assertFalse(self.module.is_available())

    def test_is_available_when_timeout_passed(self):
        # when
        self.module.available = False
        self.module.timeout = 0

        # then
        self.assertTrue(self.module.is_available())

    def test_command_success(self):
        # when
        self.module.command_function = self.module.command(lambda _: True)

        self.assertTrue(self.module.command_function(self.module))

    def test_command_failure(self):
        # when
        self.module.command_function = self.module.command(lambda _: False)

        self.assertFalse(self.module.command_function(self.module))
        self.assertFalse(self.module.is_available())

@unittest.skip("not working")
class TestModules(unittest.TestCase):

    def setUp(self):
        self.modbus = None
        self.modbus.open()

    def tearDown(self):
        self.modbus.close()

    def test_connection(self):
        self.assertTrue(self.modbus.connected)

    def test_output_board(self):
        board_id, output_board = OutputBoard.items.popitem()
        output_board.values = [1 for _ in range(OutputBoard.num_of_ports)]
        self.assertTrue(output_board.write(), True)

        output_board.values = [0 for _ in range(OutputBoard.num_of_ports)]
        self.assertTrue(output_board.write(), True)

    def test_input_board(self):
        board_id, input_board = InputBoard.items.popitem()
        self.assertTrue(input_board.read(), True)

    def test_ambient_board(self):
        board_id, ambient_board = AmbientBoard.items.popitem()
        self.assertTrue(ambient_board.read(), True)

    def test_led_light_board(self):
        board_id, led_light_board = LedLightBoard.items.popitem()
        self.assertTrue(led_light_board.write(), True)


