from timeit import default_timer as t
import serial
import logging
import time
from functools import wraps

from backend.misc.check_host import is_RPI
from backend.misc.benchmark import Benchmark


def pretty_hex(_bytes):
    return ''.join(str(_bytes))


class ModbusFunction:

    _CRC16TABLE = (
        0, 49345, 49537,   320, 49921,   960,   640, 49729, 50689,  1728,  1920,
        51009,  1280, 50625, 50305,  1088, 52225,  3264,  3456, 52545,  3840, 53185,
        52865,  3648,  2560, 51905, 52097,  2880, 51457,  2496,  2176, 51265, 55297,
        6336,  6528, 55617,  6912, 56257, 55937,  6720,  7680, 57025, 57217,  8000,
        56577,  7616,  7296, 56385,  5120, 54465, 54657,  5440, 55041,  6080,  5760,
        54849, 53761,  4800,  4992, 54081,  4352, 53697, 53377,  4160, 61441, 12480,
        12672, 61761, 13056, 62401, 62081, 12864, 13824, 63169, 63361, 14144, 62721,
        13760, 13440, 62529, 15360, 64705, 64897, 15680, 65281, 16320, 16000, 65089,
        64001, 15040, 15232, 64321, 14592, 63937, 63617, 14400, 10240, 59585, 59777,
        10560, 60161, 11200, 10880, 59969, 60929, 11968, 12160, 61249, 11520, 60865,
        60545, 11328, 58369,  9408,  9600, 58689,  9984, 59329, 59009,  9792,  8704,
        58049, 58241,  9024, 57601,  8640,  8320, 57409, 40961, 24768, 24960, 41281,
        25344, 41921, 41601, 25152, 26112, 42689, 42881, 26432, 42241, 26048, 25728,
        42049, 27648, 44225, 44417, 27968, 44801, 28608, 28288, 44609, 43521, 27328,
        27520, 43841, 26880, 43457, 43137, 26688, 30720, 47297, 47489, 31040, 47873,
        31680, 31360, 47681, 48641, 32448, 32640, 48961, 32000, 48577, 48257, 31808,
        46081, 29888, 30080, 46401, 30464, 47041, 46721, 30272, 29184, 45761, 45953,
        29504, 45313, 29120, 28800, 45121, 20480, 37057, 37249, 20800, 37633, 21440,
        21120, 37441, 38401, 22208, 22400, 38721, 21760, 38337, 38017, 21568, 39937,
        23744, 23936, 40257, 24320, 40897, 40577, 24128, 23040, 39617, 39809, 23360,
        39169, 22976, 22656, 38977, 34817, 18624, 18816, 35137, 19200, 35777, 35457,
        19008, 19968, 36545, 36737, 20288, 36097, 19904, 19584, 35905, 17408, 33985,
        34177, 17728, 34561, 18368, 18048, 34369, 33281, 17088, 17280, 33601, 16640,
        33217, 32897, 16448)

    SLAVE_ADDRESS_POS = 0
    FUNCTION_CODE_POS = 1

    NUMBER_OF_CRC_BYTES = 2
    FUNCTION_CODE_ERROR_BIT = 7

    WRITE_FUNCTIONS_CODES = {5, 6, 15, 16}
    READ_FUNCTIONS_CODES = {1, 2, 3, 4}

    def __init__(self):
        self.code = None
        self.payload_position = None

    def validate(self, slave_address, response):
        """Validate slave board response. Response can be invalid due to Slave failure or communication failure.
        Invalid response should not propragate to system. It should be ignored"""
        response_length = len(response)

        if response_length == 0:
            raise ValueError('Slave {} is not responding'.format(slave_address))

        if response_length < 5:
            raise ValueError('Slave {} response too short: {!r}'.format(slave_address, pretty_hex(response)))

        response_address = response[self.SLAVE_ADDRESS_POS]
        received_function_code = response[self.FUNCTION_CODE_POS]
        received_checksum = response[-self.NUMBER_OF_CRC_BYTES:]

        if response_length == 5:
            if received_function_code == self._set_bit_on(self.code, self.FUNCTION_CODE_ERROR_BIT):
                raise ValueError('Slave {} is indicating an error. The response is: {!r}'.format(slave_address,
                                                                                                 pretty_hex(response)))

        calculated_checksum = self._calculate_crc(response[0: - self.NUMBER_OF_CRC_BYTES])
        if received_checksum != calculated_checksum:  # check received checksum vs calculated checksum
            template = 'Slave {} checksum error. \nExcepted checksum {}\n{}'
            
            payload = response[self.payload_position: -self.NUMBER_OF_CRC_BYTES]
            response_tuple = (response_length, response_address, received_function_code, payload, received_checksum)
            text = template.format(slave_address,
                                   pretty_hex(calculated_checksum),
                                   self.pretty_response(*response_tuple))
            raise ValueError(text)

        if response_address != slave_address:  # Check if return slave address is the same
            raise ValueError('Wrong slave address: {} instead of {}. The response is: {!r}'.format(
                response_address, slave_address, pretty_hex(response)))

        if received_function_code != self.code:  # Check if return function code is the same
            raise ValueError('Wrong slave function code: {} instead of {}. The response is: {!r}'.format(
                received_function_code, self.code, pretty_hex(response)))

    @staticmethod
    def pretty_response(response_length, response_address, received_function_code, payload, received_checksum):
        """Formats response in a pleasent readable way"""
        return """Recived checksum: {}
        Frame length: {}
        Address: {}
        Function code: {}
        Payload: {}
        \n""".format(pretty_hex(received_checksum),
                     response_length,
                     response_address,
                     received_function_code,
                     pretty_hex(payload), )

    @staticmethod
    def _set_bit_on(val, bit_num):
        """Sets bit on desired position"""
        return val | (1 << bit_num)

    def _calculate_crc(self, inputstring):
        """Calculates cyclic redundance cheskum.
        Thanks to CRC it is easy to recognize if communication packet is corrupted"""
        register = 0xFFFF  # Preload a 16-bit register with ones

        for char in inputstring:
            register = (register >> 8) ^ self._CRC16TABLE[(register ^ char) & 0xFF]
        return ModbusFunction._num_to_two_bytes(register, lsb_first=True)

    def _list_to_byte_string(self, _list):
        """Converts list with integer values to binary string"""
        bytestring = b""
        for value in _list:
            bytestring += self._num_to_two_bytes(value)

        return bytestring

    @staticmethod
    def _byte_string_to_list(byte_string):
        """Converts binary string into list o values"""
        values = []
        two_bytes = [0, 0]
        for byte_num, byte in enumerate(byte_string):
            two_bytes[byte_num % 2] = byte
            if byte_num % 2 == 1:
                values.append(ModbusFunction._two_bytes_to_num(two_bytes))
                two_bytes = [0, 0]
        return values

    @staticmethod
    def _two_bytes_to_num(two_bytes):
        """Converts two bytes list to integer number"""
        return two_bytes[0]*256 + two_bytes[1]

    @staticmethod
    def _num_to_two_bytes(value, lsb_first=False):
        """Converts integer number to two bytes list.
        List may be least siginifican byte first or most significant byte first"""
        msb = value >> 8
        lsb = value & 255

        if lsb_first:
            return bytes([lsb, msb]) 
        else:
            return bytes([msb, lsb])

    @staticmethod
    def slave_address_and_crc(modbus_fun):
        """Decorator that wraps every modbus function run method.
            It adds at the begging of the request slave address, modbus function code.
            It adds at the enf of the request CRC"""
        @wraps(modbus_fun)
        def function_wrapper(self, slave_address, *modbus_fun_args):
            request = bytes([slave_address, self.code])  # slave address
            fun_request_part, num_of_bytes_to_read = modbus_fun(self, *modbus_fun_args)  # function specific part of request
            request += fun_request_part
            request += self._calculate_crc(request)

            return request, num_of_bytes_to_read

        return function_wrapper

    def __repr__(self, ):
        return self.__class__.__name__ + " code: " + str(self.code)


class ReadRegsFunction(ModbusFunction):
    def __init__(self):
        super().__init__()
        self.min_request_bytes = 5
        self.min_response_bytes = 5
        self.code = 3
        self.payload_position = 3

    @ModbusFunction.slave_address_and_crc
    def run(self, start_reg_num, end_reg_num):
        num_of_regs = end_reg_num - start_reg_num + 1
        request = self._num_to_two_bytes(start_reg_num)
        request += self._num_to_two_bytes(num_of_regs)
        
        number_of_bytes_to_read = self.min_request_bytes + 2*num_of_regs      
        return request, number_of_bytes_to_read

    def get_payload(self, response):
        return self._byte_string_to_list(response[self.payload_position: -self.NUMBER_OF_CRC_BYTES])


class WriteRegsFunction(ModbusFunction):

    def __init__(self):
        super().__init__()
        self.min_request_bytes = 9
        self.min_response_bytes = 8
        self.code = 16
        self.payload_position = 2

    @ModbusFunction.slave_address_and_crc
    def run(self, start_reg_num, values):
        
        num_of_regs = len(values)
        byte_count = num_of_regs*2 

        request = self._num_to_two_bytes(start_reg_num)
        request += self._num_to_two_bytes(num_of_regs)
        request += bytes([byte_count])
        request += self._list_to_byte_string(values)

        return request, self.min_response_bytes


class WriteCoilsFunction(ModbusFunction):

    def __init__(self):
        super().__init__()
        self.min_request_bytes = 11
        self.min_response_bytes = 8
        self.code = 15
        self.payload_position = 2

    @ModbusFunction.slave_address_and_crc
    def run(self, start_coil_num, values):
        
        num_of_coils = len(values)
        out_bytes = self._coils_vals_to_bytes(values)
        byte_count = len(out_bytes)

        request = self._num_to_two_bytes(start_coil_num)
        request += self._num_to_two_bytes(num_of_coils)
        request += bytes([byte_count])
        request += out_bytes

        return request, self.min_response_bytes

    @staticmethod
    def _coils_vals_to_bytes(values):
        """converts coils values to bytes"""
        if not values:
            return bytes([0, 0])

        out_bytes = bytes([])
        byte = 0
        byte_iter = 0
        for coil_val in values:
            if coil_val:
                byte |= 1 << byte_iter
            byte_iter += 1
            if byte_iter == 8:
                out_bytes += bytes([byte])
                byte = 0
                byte_iter = 0

        if byte_iter < 7:  # didn't iterated through whole byte

            if len(out_bytes) % 2:
                out_bytes += bytes([byte])  # add pending byte
            else:
                out_bytes += bytes([byte, 0])  # add pennding byte and zero byte for odd len bytes
        else:  # iterated through whole byte
            if len(out_bytes) % 2:  # even number of whole bytes
                out_bytes += bytes([0])  # add pending byte

        return out_bytes


class ModbusNetwork:
    """Handles opening and closing of serial port.
       Gives API to modbus functions"""

    _instance = None
    _is_initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not ModbusNetwork._is_initialized:
            ModbusNetwork._is_initialized = True
            self.logger = logging.getLogger('MODBUS')

            self.baudrate = 38400
            self.connected = False
            self.port = ""
            self.t_3_5 = 1e-3  # (1/baudrate)*9*3.5 # 9 bits per charater. 3.5 characters time sleep
            self.sleep_timer = 0
            self.correct_frames = 0
            self.corrupted_frames = 0
            self.consecutive_corrupted_frames = 0

            self.bench = Benchmark(self.logger.level)
            self.bench.start()

            if is_RPI:
                self.port = "/dev/ttyUSB0"
            else:
                self.port = "COM4"

            self.serial_port = None

            self.read_regs_obj = ReadRegsFunction()
            self.write_regs_obj = WriteRegsFunction()
            self.write_coils_obj = WriteCoilsFunction()

    def open(self):
        try:
            self.serial_port = serial.Serial(port=self.port,
                                        baudrate=self.baudrate,
                                        timeout=0.02,
                                        parity=serial.PARITY_NONE,
                                        stopbits=1)
            self.connected = True
            return True
        except serial.SerialException:
            self.logger.error("Can't open port {}".format(self.port))
            return False

    def is_available(self):
        if self.consecutive_corrupted_frames > 1:
            return False
        else:
            return True

    def reload(self):
        self.close()
        self.open()
        self.consecutive_corrupted_frames = 0
        self.logger.warn("Serial reload")

    def close(self):
        self.serial_port.close()
        self.connected = False

    def write_regs(self, slave_address, start_reg_num, values):
        return self.run(self.write_regs_obj, slave_address, start_reg_num, values)

    def write_coils(self, slave_address, start_coil_num, values):
        return self.run(self.write_coils_obj, slave_address, start_coil_num, values)

    def read_regs(self, slave_address, start_reg_num, end_reg_num):
        return self.run(self.read_regs_obj, slave_address, start_reg_num, end_reg_num)

    def run(self, func_obj, slave_address, *modbus_fun_args):
        """ Wrapper for run functions of modbus functions.
            It expect function's request part and number of bytes to read .
            "It embedes function request with slave address, fun code, crc.
            Then it performs write and read, validates response and return either payload or ack, nack.
        """

        request, num_of_bytes_to_read = func_obj.run(slave_address, *modbus_fun_args)  #
        sleep_time = t() - self.sleep_timer
        if sleep_time < self.t_3_5:  # if there wasn't enaugh silent time, sleep!
            time.sleep(sleep_time)

        self.serial_port.write(request)
        response = self.serial_port.read(num_of_bytes_to_read)

        self.sleep_timer = t()

        try:
            func_obj.validate(slave_address, response)
        except ValueError as e:
            self.logger.warn(e)
            self.corrupted_frames += 1
            self.consecutive_corrupted_frames += 1
            return False
        else:
            self.correct_frames += 1
            if func_obj.code in ModbusFunction.READ_FUNCTIONS_CODES:  # return payload
                return func_obj.get_payload(response)

            return True  # return ack

    def debug(self,):
        if self.bench.loops_per_second():
            self.logger.debug("\nCorrect frames: {}\nCorrupted frames: {}".format(self.correct_frames,
                                                                                  self.corrupted_frames))

