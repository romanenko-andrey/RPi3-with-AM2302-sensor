import TK4S_RS485_LIB as RS485
import time
import ConfigParser
import work_with_db as db

Config = ConfigParser.ConfigParser()

def set_preheat_temp():
  Config.read("/var/www/lab_app/settings.ini")
  set_temperature = Config.getint("StageOne", "set_temp")
  max_preheat_power_value = Config.getint("StageOne", "max_preheat_power_value")
  
  print "try to set temperature = " + str(set_temperature) 
  if RS485.writes_SV(set_temperature) == False:
    print "set_preheat_temp() --> error set SV = ", set_temperature
    return {'state': 'error', 
            'msg' : "Error write temperature = " + 
            str(set_temperature) + 
            " to TK4S. Check the connection and try again..."}          
  
  print "try to set maximum power value = " + str(max_preheat_power_value) 
  attempt = RS485.MAX_ATTEMPTS   
  while attempt > 0:
    if (RS485.write_max_output_value(max_preheat_power_value) == True):
      db.add_new_log_to_and("PREHEAT", db.SAVE_START_TIME, db.DONT_SAVE_PICTURE, "preheat on")
      return {'state': 'ok', 'msg' : 'The preheating is starting now.'}
    attempt -= 1
  print "set_preheat_temp() --> error set maximum power value = ", max_preheat_power_value  
  return {'state': 'error', 
          'msg' : "Error write maximum power value = " + 
          str(max_preheat_power_value) + 
          " to TK4S. Check the connection and try again..."}      
  

