def cooling():
  import subprocess
  import json
  import work_with_db as db
  import time
  
  #STOP ALL BOTS
  id, status, current_temp, start_time_str, start_temp = db.get_last_log()
  
  db.add_new_log(id,"STOP", current_temp, current_temp,
                 db.SAVE_START_TIME, db.DONT_SAVE_PICTURE, "stop heating")
                 
  time.sleep(3)
  db.add_new_log(id,"COOLING", current_temp, current_temp, 
                 db.SAVE_START_TIME, db.DONT_SAVE_PICTURE, "cooling")
  time.sleep(1)
  subprocess.Popen(["/var/www/lab_app/venv/bin/python", '/var/www/lab_app/tk4s-bot.py'])
  return {'state': 'ok', 
          'msg' : "Start cooling to safe temperature"}