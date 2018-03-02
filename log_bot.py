import time
import work_with_db as db
import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read("/var/www/lab_app/settings.ini")
log_interval = Config.getint('General', 'log_interval')
start_photo_temp = Config.getint('StageTwo', 'start_photo_temp')
max_temp = Config.getint('StageTwo', 'max_temp')

start_time = time.time()
print '!!!!!!!!!!!!! START LOG_BOT !!!!!!!!!!!!!'

while True:
  i = log_interval
  while i > 0:
    i -= 1
    id, status, temp, start_temp, start_time  = db.get_last_log()
    if status == "STOP" or status == "COOLING" or temp >= max_temp:
      print '!!!!!!!!!!!!! STOP LOG_BOT !!!!!!!!!!!!!!!!'
      db.add_new_log(id, status, db.DONT_SAVE_START_TIME, db.SAVE_PICTURE) 
      exit()
    time.sleep(1)  
    
  if temp > start_photo_temp:
    db.add_new_log(id, status, db.DONT_SAVE_START_TIME, db.SAVE_PICTURE) 
  else:
    db.add_new_log(id, status, db.DONT_SAVE_START_TIME, db.DONT_SAVE_PICTURE) 

  