import TK4S_RS485_LIB as RS485

def stop_heater():
  attempt = 5   
  while attempt > 0:
    if (RS485.write_SV(0) == True):
       return {'state': 'ok', 'msg' : 'The heater was succefully stopped.'}
    attempt -= 1
    
  return {'state': 'error', 
          'msg' : "Error write to TK4S. Check the connection and try again..."}