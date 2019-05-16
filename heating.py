def heating(start_photo_temp):
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
  db.add_new_log_to_and("STOP", db.SAVE_START_TIME, db.DONT_SAVE_PICTURE, 0, 0, "stop heating")
  time.sleep(3)
 
  print "START ANALYSIS. Try to set maximum power value = ", max_power_value, "%"
  attempt = RS485.MAX_ATTEMPTS   
  while attempt > 0:
    if (RS485.write_max_output_value(max_power_value) == True):
      print "Ok"
      break
    attempt -= 1
  
  pv = RS485.reads_PV()
  if type(pv) is str:
    print "error read PV"
    pv = 0
    
  sv = RS485.reads_SV()
  if type(sv) is str:
    print "error read SV"
    sv = 0  
    
  #START ALL BOTS
  db.add_new_log_to_and("HEATING", db.SAVE_START_TIME, db.DONT_SAVE_PICTURE, pv, sv, "start analysis")
  time.sleep(0.5)   
  #subprocess.Popen(["/var/www/lab_app/venv/bin/python", 
  #                  '/var/www/lab_app/log_bot.py', start_photo_temp])
  
  subprocess.Popen(["/var/www/lab_app/venv/bin/python", '/var/www/lab_app/tk4s-bot.py'])
  
  print 'json was send .....'
  return {'state': 'ok', 
          'msg' : "Analysis was running successfully"}