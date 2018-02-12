import TK4S_RS485_LIB as RS485
import time
import ConfigParser

Config = ConfigParser.ConfigParser()

def set_preheat_temp():
  Config.read("/var/www/lab_app/settings.ini")
  set_temperature = Config.getint("StageOne", "set_temp")
  print "try to set temperature = " + str(set_temperature) 
  attempt = 5   
  while attempt > 0:
    if (RS485.write_SV(set_temperature) == True):
       return {'state': 'ok', 'msg' : 'The preheating is starting now.'}
    attempt -= 1
    
  return {'state': 'error', 
          'msg' : "Error write temperature = " + 
          str(set_temperature) + 
          " to TK4S. Check the connection and try again..."}
           



