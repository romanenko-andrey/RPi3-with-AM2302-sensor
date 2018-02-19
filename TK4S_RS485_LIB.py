#in config.txt need to correct the processor freq for change baudrate 
#core_freq=258
#enable_uart=1

import serial
import time
from PyCRC.CRC16 import CRC16

#port = serial.Serial("/dev/ttyS0", baudrate=9600, stopbits=2, timeout=1)
port = serial.Serial()
port.port = "/dev/ttyS0"
port.baudrate = 9600
port.stopbits = 2
port.timeout = 1

#maximum test for read or write params to port
MAX_ATTEMPTS = 5

req_read_PV  = bytearray([0x01, 0x04, 0x03, 0xE8, 0x00, 0x01, 0xB1, 0xBA])
req_set_1100 = bytearray([1, 6, 0, 0x39, 4, 0x4c, 0x5a, 0xf2])
req_read_SV  = bytearray([0x01, 0x04, 0x03, 0xEB, 0x00, 0x01, 0x41, 0xBA])
req_save_SV  = bytearray([0x01, 0x06, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00])
req_save_MV  = bytearray([0x01, 0x06, 0x00, 0x72, 0x00, 0x00, 0x00, 0x00])

CRC_ERROR_MSG = "CRC error" 
PKG_SIZE_ERROR_MSG = "error package size"
PORT_ERROR_MSG = "Serial port open error"
ERROR_READ_SV = 'Error: cannot read SV from TK4S'
ERROR_READ_PV = 'Error: cannot read PV from TK4S'

def read_SV():
  try:
    port.open()
    port.write(req_read_SV)
    rcv = port.read(7)
    port.close()
  except:
    port.close()
    return PORT_ERROR_MSG
      
  rez = bytearray(rcv)
  crc16 = CRC16( modbus_flag = True ).calculate(rcv[0:5])
  if len(rez) == 7:
    crc = rez[6] * 256 + rez[5] 
    if crc == crc16:
      return rez[3] * 256 + rez[4]
    else:
      return CRC_ERROR_MSG   
  else: 
    return PKG_SIZE_ERROR_MSG

def read_PV():
  try:
    port.open()
    port.write(req_read_PV)
    rcv = port.read(7)
    port.close()
  except:
    port.close()
    return PORT_ERROR_MSG  
  
  rez = bytearray(rcv)
  crc16 = CRC16( modbus_flag = True ).calculate(rcv[0:5])
  if len(rez) == 7:
    crc = 256*rez[6] + rez[5] 
    if crc == crc16:
      return 256*rez[3] + rez[4]
    else:
      return CRC_ERROR_MSG     
  else: 
    return PKG_SIZE_ERROR_MSG
 
def write_SV(sv):
  req_save_SV[4] = int(sv) // 256
  req_save_SV[5] = int(sv) % 256
  crc16 = CRC16( modbus_flag = True ).calculate( str(req_save_SV[0:6]) )
  req_save_SV[6] = crc16 % 256
  req_save_SV[7] = crc16 // 256
  try:
    port.open()
    port.write(req_save_SV)
    rcv = port.read(8)
    port.close()
  except:
    port.close()
    return PORT_ERROR_MSG     
    
  rez = bytearray(rcv)
  if rez == req_save_SV:
    return True    
  else: 
    print "Error send SV = ", sv
    return False

def write_max_output_value(sv):
  req_save_MV[4] = int(sv) // 256
  req_save_MV[5] = int(sv) % 256
  crc16 = CRC16( modbus_flag = True ).calculate( str(req_save_MV[0:6]) )
  req_save_MV[6] = crc16 % 256
  req_save_MV[7] = crc16 // 256
  try:
    port.open()
    port.write(req_save_MV)
    rcv = port.read(8)
    port.close()
  except:
    port.close()
    return PORT_ERROR_MSG     
    
  rez = bytearray(rcv)
  if rez == req_save_MV:
    return True    
  else: 
    print "Error send MV = ", sv
    return False
    
def reads_SV():
  sv = read_SV()
  attempt = MAX_ATTEMPTS
  while attempt > 0 and type(sv) is str:
    attempt -= 1
    sv = read_SV()
    time.sleep(0.05)
  if attempt == 0 and type(sv) is str:
    return ERROR_READ_SV
  return sv
  
def reads_PV():
  pv = read_PV()
  attempt = MAX_ATTEMPTS
  while attempt > 0 and type(pv) is str:
    attempt -= 1
    pv = read_PV()
    time.sleep(0.05)
  if attempt == 0 and type(pv) is str:
    return ERROR_READ_PV
  return pv