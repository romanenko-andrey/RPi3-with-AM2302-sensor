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
MAX_ATTEMPTS = 10
TIME_BETWEEN_REPEAT = 0.05
TIME_AFTER_PORT_OPEN = 0.01
 
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
ERROR_WRITE_SV = 'Error: cannot write SV to TK4S'
TEMPERATURE_ERROR_MSG = 'Error: the temperaure is out of range = 0 .. 1600'

def bytes_to_str(rcv):
  arr = bytearray(rcv)
  s = []
  for b in arr:
    s.append( str(b) )
  return s  
  

def open_port_and_read(request, n):
  try:
    #print "-----------" 
    port.open()
    time.sleep(TIME_AFTER_PORT_OPEN)
    port.write(request)
    rcv = port.read(n)
    print "-->", bytes_to_str(request), "  <--", bytes_to_str(rcv)
    port.close()
    return rcv
  except:
    port.close()
    return False

def check_crc_n7(rcv):
  rez = bytearray(rcv)
  crc16 = CRC16( modbus_flag = True ).calculate(rcv[0:5])
  if len(rez) == 7:
    crc = rez[6] * 256 + rez[5] 
    if crc == crc16:
      res = 256*rez[3] + rez[4]
      if res > 1600:
        return TEMPERATURE_ERROR_MSG
      else:
        return res
    else:
      return CRC_ERROR_MSG   
  else: 
    return PKG_SIZE_ERROR_MSG

    
def read_SV():
  print "try to read_SV"
  rcv = open_port_and_read(req_read_SV, 7)
  if rcv == False:
    return PORT_ERROR_MSG
  else:
    return check_crc_n7(rcv)    
  

def read_PV():
  print "try to read_PV"
  rcv = open_port_and_read(req_read_PV, 7)
  if rcv == False:
    return PORT_ERROR_MSG
  else:
    return check_crc_n7(rcv)    
  
 
def write_SV(sv):
  req_save_SV[4] = int(sv) // 256
  req_save_SV[5] = int(sv) % 256
  crc16 = CRC16( modbus_flag = True ).calculate( str(req_save_SV[0:6]) )
  req_save_SV[6] = crc16 % 256
  req_save_SV[7] = crc16 // 256
  
  print "try to write_SV ", sv
  rcv = open_port_and_read(req_save_SV, 8)
  if rcv == False:
    return PORT_ERROR_MSG
  else:    
    rez = bytearray(rcv)
    if rez != req_save_SV:
      #print "Error send SV = ", sv
      return False    
  return True

def write_max_output_value(sv):
  req_save_MV[4] = int(sv) // 256
  req_save_MV[5] = int(sv) % 256
  crc16 = CRC16( modbus_flag = True ).calculate( str(req_save_MV[0:6]) )
  req_save_MV[6] = crc16 % 256
  req_save_MV[7] = crc16 // 256
  
  print "try to write_output_power MV ", sv
  rcv = open_port_and_read(req_save_MV, 8)
  if rcv == False:
    return PORT_ERROR_MSG
    
  rez = bytearray(rcv)
  if rez == req_save_MV:
    return True    
  else: 
    #print "Error send MV = ", sv
    return False
    
def reads_SV():
  sv = read_SV()
  attempt = MAX_ATTEMPTS
  while attempt > 0 and type(sv) is str:
    attempt -= 1
    sv = read_SV()
    time.sleep(TIME_BETWEEN_REPEAT)
  if attempt == 0 and type(sv) is str:
    #print "Error read SV = ", sv
    return ERROR_READ_SV
  return sv
  
def reads_PV():
  pv = read_PV()
  attempt = MAX_ATTEMPTS
  while attempt > 0 and type(pv) is str:
    attempt -= 1
    pv = read_PV()
    time.sleep(TIME_BETWEEN_REPEAT)
  if attempt == 0 and type(pv) is str:
    #print "Error read PV = ", pv
    return ERROR_READ_PV
  return pv

def writes_SV(sv):
  attempt = MAX_ATTEMPTS
  while write_SV(sv) == False and attempt > 0:
    attempt -= 1
    time.sleep(TIME_BETWEEN_REPEAT)
  if attempt == 0:
    #print "Error write SV = ", sv
    return ERROR_WRITE_SV
  return True 
  
  