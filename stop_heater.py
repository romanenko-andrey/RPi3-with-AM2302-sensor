import TK4S_RS485_LIB as RS485
import work_with_db as db

def stop_heater():
  attempt = 5   
  while attempt > 0:
    if (RS485.write_SV(0) == True):
       db.add_new_log_to_and("STOP", True, False, "oven off")
       return {'state': 'ok', 'msg' : 'The heater was succefully stopped.'}
    attempt -= 1
    
  return {'state': 'error', 
          'msg' : "Error write to TK4S. Check the connection and try again..."}