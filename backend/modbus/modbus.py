import serial
import logging
from functools import wraps

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

def _list_to_byte_string(list):
               
    bytestring = b""
    for value in list:
        bytestring += _num_to_two_bytes_str(value)

    return bytestring

def _byte_string_to_list(bytestring):
    """Converts packed byte string into list o values"""
    values = []
    two_bytes = [0, 0]
    for byte_num, byte in enumerate(bytestring):
        two_bytes[byte_num%2] = byte
        if byte_num%2 == 1:
            values.append(_two_byte_str_to_num(two_bytes))
            two_bytes = [0, 0]
    return values

def _two_byte_str_to_num(byte_string):
    return byte_string[0]*256 + byte_string[1] 

def _num_to_two_bytes_str(value, LsbFirst=False):

    msb = value >> 8
    lsb = value & 255

    if LsbFirst:
        return bytes([lsb, msb]) 
    else:
        return bytes([msb, lsb]) 
    
def _calculate_crc(inputstring):
 
    # Preload a 16-bit register with ones
    register = 0xFFFF

    for char in inputstring:
        register = (register >> 8) ^ _CRC16TABLE[(register ^ char) & 0xFF]
    return _num_to_two_bytes_str(register, LsbFirst=True)

def run_fun(func):
    """ Wrapper for run functions of modbus functions. 
        It expect function's request part and number of bytes to read .
        "It embedes function request with slave address, fun code, crc.
        Then it performs write and read and returns response.
    """
    @wraps(func)
    def func_wrapper(self, serial, slave_address, *args, **kwargs):
        request = bytes([slave_address, self.code]) # slave address
        fun_request_part, num_of_bytes_to_read = func(self, serial, slave_address, *args) # function specific part of request
        request += fun_request_part
        request += _calculate_crc(request)

        serial.write(request)

        response = serial.read(num_of_bytes_to_read)
        return response
            
    return func_wrapper

class Read_regs_function():
    def __init__(self, ):
        self.min_request_bytes = 5
        self.min_response_bytes = 5
        self.code = 3
        self.payload_position = 3

    @run_fun
    def run(self, serial, slave_address, start_reg_num, end_reg_num):
        num_of_regs = end_reg_num - start_reg_num + 1
        request = _num_to_two_bytes_str(start_reg_num)
        request += _num_to_two_bytes_str(num_of_regs)
        
        number_of_bytes_to_read = self.min_request_bytes + 2*num_of_regs      
        return request, number_of_bytes_to_read

    def __repr__(self,):
        return "Function 3 - read registers"

class Write_regs_function():
    def __init__(self, ):
        self.min_request_bytes = 9
        self.min_response_bytes = 8
        self.code = 16

    @run_fun
    def run(self, serial, slave_address, start_reg_num, values):
        
        num_of_regs = len(values)
        byte_count = num_of_regs*2

        request = _num_to_two_bytes_str(start_reg_num)
        request += _num_to_two_bytes_str(num_of_regs)
        request += _num_to_two_bytes_str(byte_count)
        request += _list_to_byte_string(values)

        return request, self.min_response_bytes

class Write_coils_function():

    def __init__(self, ):
        self.min_request_bytes = 11
        self.min_response_bytes = 8
        self.code = 15

    @run_fun
    def run(self, slave_address, start_coil_num, values):
        
        num_of_coils = len(values)
        byte_count = num_of_regs*2

        request = _num_to_two_bytes_str(start_coil_num)
        request += _num_to_two_bytes_str(num_of_coils)
        request += _num_to_two_bytes_str(byte_count)
        request += self._coils_vals_to_bytes(values)

        return response, self.min_response_bytes

    def _coils_vals_to_bytes(self, values):

        bytes = ""
        byte = 0
        byte_iter = 7
        for coil_val in values:
            if coil_val:
                byte |= 1<<byte_iter

            byte_iter -= 1
            if byte_iter == -1:
                bytes += chr(byte)
                byte = 0
                byte_iter = 7

        return bytes

class Modbus():

    BYTEPOSITION_FOR_SLAVEADDRESS   = 0
    BYTEPOSITION_FOR_FUNCTIONCODE   = 1
    BYTEPOSITION_FOR_FUNCTIONCODE   = 1

    NUMBER_OF_RESPONSE_STARTBYTES   = 2
    NUMBER_OF_CRC_BYTES = 2
    BITNUMBER_FUNCTIONCODE_ERRORINDICATION = 7

    def __init__(self, port, bauderate):
        self.logger = logging.getLogger('MODBUS')

        self.port = port
        self.bauderate = bauderate
        self.connected = False
        try:
            self.serial =  serial.Serial(port=port, baudrate=bauderate, timeout=0.02, parity=serial.PARITY_NONE)
            self.connected = True
        except serial.SerialException:
            self.logger.error("Can't open port {}".format(port))

        self.read_regs_obj = Read_regs_function()
        self.write_regs_obj = Write_regs_function()
        self.write_coils_obj = Write_coils_function()

    def write_regs(self, slave_address, start_reg_num, values):
        response = self.write_regs_obj.run(self.serial, slave_address, start_reg_num, values)

        try:
            self._validate_response(slave_address, response, self.write_regs_obj)
        except ValueError as e:
            self.logger.debug(e)
            return False
        else:
            return True

    def write_coils(self, slave_address, start_coil_num, values):
        response = self.write_coils_obj.run(self.serial, slave_address, start_coil_num, values)
        try:
            self._validate_response(slave_address, response, self.write_coils_obj)
        except ValueError as e:
            self.logger.debug(e)
            return False
        else:
            return True

    def read_regs(self, slave_address, start_reg_num, end_reg_num):

        response = self.read_regs_obj.run(self.serial, slave_address, start_reg_num, end_reg_num)

        try:
            self._validate_response(slave_address, response, self.read_regs_obj)
        except ValueError as e:
            self.logger.warn(e)
            return False
        else:
            payload = _byte_string_to_list(response[self.read_regs_obj.payload_position : -Modbus.NUMBER_OF_CRC_BYTES])
            return payload

    def _validate_response(self, slave_address, response, function):

        #check frame length
        if len(response) == 0:
            raise ValueError('Slave {} is not responding'.format(slave_address))

        if len(response) < function.min_response_bytes:
            raise ValueError('Slave {} returns too short response: {!r}'.format(slave_address, response))

        #check checksum equility
        received_checksum = response[-Modbus.NUMBER_OF_CRC_BYTES:]
        response_without_checksum = response[0 : len(response) - Modbus.NUMBER_OF_CRC_BYTES]
        calculated_checksum = _calculate_crc(response_without_checksum)

        if received_checksum != calculated_checksum:
            template = 'Slave {} checksum error. The response is: {!r}'
            text = template.format(slave_address, response)
            raise ValueError(text)

        # Check slave address
        response_address = response[Modbus.BYTEPOSITION_FOR_SLAVEADDRESS]

        if response_address != slave_address:
            raise ValueError('Wrong return slave address: {} instead of {}. The response is: {!r}'.format( \
                responseaddress, slaveaddress, response))

        # Check function code
        received_function_code = response[Modbus.BYTEPOSITION_FOR_FUNCTIONCODE]

        if received_function_code == self.__set_bit_on(function.code, Modbus.BITNUMBER_FUNCTIONCODE_ERRORINDICATION):
            raise ValueError('Slave {} is indicating an error. The response is: {!r}'.format(slave_address, response))

        elif received_function_code != function.code:
            raise ValueError('Slave {} wrong functioncode: {} instead of {}. The response is: {!r}'.format( \
                slave_address, received_function_code, function.code, response))

    def __set_bit_on(self, val, bit_num):
        return val | (1 << bit_num)
        pass


