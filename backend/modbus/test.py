#import serial
#import time
#import binascii
#ser =  serial.Serial(port='COM7', baudrate=57600, timeout=0, parity=serial.PARITY_NONE)




##ser.write(b'aaaaaaaaaaaaaaaaaaaaaaaaaaaa')
##msg = []
##num_of_msg = 0
##while ser.in_waiting:
##    msg.append(ser.read(1))
##    num_of_msg += 1
    
##msg = [s.decode() for s in msg]
##print (msg)
##print ('num_of_msg ', num_of_msg)
##ser.close()

#from timeit import default_timer as t
#import time
#import minimalmodbus
#instr = minimalmodbus.Instrument('COM7', 1)
#time.sleep(1)
#num_of_regs = 50
#num_of_tests = 10
#for i in range(num_of_tests):
#    print ("test num: ", i)
#    #try:
#    #    start = t()
#    #    for i in range(num_of_regs):
#    #        a = instr.read_register(i)

#    #    print (t()-start)
#    #except:
#    #    print ('error')
#    #    pass


#    try:
#        start = t()
#        a = instr.read_registers(0, num_of_regs)

#        print ('calosc: ',t()-start)
#    except:
#        print ('error')
#        pass

#    time.sleep(0.5)


#import struct
#from ctypes import c_uint16 as uint16

#def _num_to_two_bytes_str(value, LsbFirst=False):

#    if LsbFirst:
#        formatcode = '<'  # Little-endian
#    else:
#        formatcode = '>'  # Big-endian
#    formatcode += 'H'
#    outstring = _pack(formatcode, value)
#    assert len(outstring) == 2
#    return outstring

#def _pack( formatstring, value):


#    try:
#        result = struct.pack(formatstring, value)
#    except:
#        errortext = 'The value to send is probably out of range, as the num-to-bytestring conversion failed.'
#        errortext += ' Value: {0!r} Struct format code is: {1}'
#        raise ValueError(errortext.format(value, formatstring))

#    return str(result, encoding='latin1')  # Convert types to make it Python3 compatible

#def _two_byte_str_to_num( bytestring):

#    formatcode = '>H'  # Big-endian
#    fullregister = _unpack(formatcode, bytestring)

#    return fullregister 


#def _unpack( formatstring, packed):

#    packed = bytes(packed, encoding='latin1')  # Convert types to make it Python3 compatible

#    try:
#        value = struct.unpack(formatstring, packed)[0]
#    except:
#        errortext = 'The received bytestring is probably wrong, as the bytestring-to-num conversion failed.'
#        errortext += ' Bytestring: {0!r} Struct format code is: {1}'
#        raise ValueError(errortext.format(packed, formatstring))

#    return value

#def _byte_string_to_list( bytestring):

#    values = []
#    two_bytes = ""
#    for byte_num, byte in enumerate(bytestring):
#        two_bytes += byte
#        if byte_num%2 == 1:
#            values.append(_two_byte_str_to_num(two_bytes))
#            two_bytes = ""
#    return values

#vals = [1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1]

#def _coils_vals_to_bytes(values):

#    bytes = ""
#    BITS_IN_BYTE = 8
#    byte = 0
#    byte_iter = 7
#    for coil_val in values:
#        if coil_val:
#            byte |= 1<<byte_iter

#        byte_iter -= 1
#        if byte_iter == -1:
#            bytes += chr(byte)
#            byte = 0
#            byte_iter = 7
#    return bytes

#_coils_vals_to_bytes(vals)


#def _num_to_two_bytes_str(value, LsbFirst=False):

#    msb = value >> 8
#    lsb = value & 255

#    if LsbFirst:
#        return chr(lsb) + chr(msb)
#    else:
#        return chr(msb) + chr(lsb)
    
#def _two_byte_str_to_num(byte_string):
#    value = ord(byte_string[0])*256 + ord(byte_string[1])
#    return value 

from backend.modbus.modbus import Modbus
from time import sleep
from timeit import default_timer as t
modbus = Modbus('COM7', 1000000)


regs_to_write = [i for i in range(15)] 
sleep(2)
all_start = t()
for i in range(10):
    start = t()
    a =  (modbus.read_regs(1, 0, 20))
    print ('t: ', t()-start)


print ('all: ', t()-all_start)
