def heating():
  import work_with_db as db
  import subprocess
  import json
  import time
  import TK4S_RS485_LIB as RS485
  import ConfigParser
  
  Config = ConfigParser.ConfigParser()
  Config.read("/var/www/lab_app/settings.ini")
  max_power_value = Config.getint("StageTwo", "max_power_value")
  
  
  #STOP ALL BOTS
  db.add_new_log_to_and("STOP", True, False, "stop heating")
  time.sleep(3)
  #START ALL BOTS
  db.add_new_log_to_and("HEATING", True, False, "start analysis")
  time.sleep(0.5) 
  subprocess.Popen(["/var/www/lab_app/venv/bin/python", '/var/www/lab_app/log_bot.py'])
  subprocess.Popen(["/var/www/lab_app/venv/bin/python", '/var/www/lab_app/tk4s-bot.py'])
  
  print "try to set maximum power value = ", max_power_value, "%"
  attempt = RS485.MAX_ATTEMPTS   
  while attempt > 0:
    if (RS485.write_max_output_value(max_power_value) == True):
      print "Ok"
      break
    attempt -= 1
  
  print 'json was send .....'
  return {'state': 'ok', 
          'msg' : "Analysis was running successfully"}