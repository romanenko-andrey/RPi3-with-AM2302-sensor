def cooling():
  import subprocess
  import json
  import work_with_db as db
  import time
  
  #STOP ALL BOTS
  db.add_new_log_to_and("STOP", True, False, "stop heating")
  time.sleep(3)
  db.add_new_log_to_and("COOLING", True, False, "cooling")
  time.sleep(1)
  subprocess.Popen(["/var/www/lab_app/venv/bin/python", '/var/www/lab_app/tk4s-bot.py'])
  return {'state': 'ok', 
          'msg' : "Start cooling to safe temperature"}