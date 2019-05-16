import time
import work_with_db as db
import TK4S_RS485_LIB as RS485
import ConfigParser
import sys
import RPi.GPIO as GPIO

Config = ConfigParser.ConfigParser()
Config.read("/var/www/lab_app/settings.ini")
log_interval = Config.getint('General', 'log_interval')
start_photo_temp = Config.getint('StageTwo', 'start_photo_temp')
max_temp = Config.getint('StageTwo', 'max_temp')



if (len(sys.argv) >= 2):
  try:
     start_photo_temp = int( sys.argv[1] )
  except:
	 start_photo_temp = 900
	 
start_time = time.time()
print '!!!!!!!!!!!!! START LOG_BOT !!!!!!!!!!!!!'
print "start_photo_temp = ", start_photo_temp  


while True:
  i = log_interval
  while i > 0:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(EXIT_PIN, GPIO.IN,  pull_up_down=GPIO.PUD_UP)
     
    i -= 1
    id, status, temp, start_temp, start_time  = db.get_last_log()
    if status == "STOP" or status == "COOLING" or not GPIO.input(EXIT_PIN):
      print '!!!!!!!!!!!!! STOP LOG_BOT !!!!!!!!!!!!!!!!'
      #db.add_new_log(id, status, db.DONT_SAVE_START_TIME, db.SAVE_PICTURE) 
      exit()
    time.sleep(1)  
    
    if temp > max_temp:
      #COOLING START
      db.add_new_log_to_and("COOLING", db.SAVE_START_TIME, db.DONT_SAVE_PICTURE, temp, temp, "stop heating")
  
  pv = RS485.reads_PV()
  if type(pv) is str:
    print "error read PV"
    pv = temp
    
  sv = RS485.reads_SV()
  if type(sv) is str:
    print "error read SV"
    sv = temp  
  
  print "write LOG to disk ...."
  if temp > start_photo_temp:
    db.add_new_log(id, status, pv, sv, db.DONT_SAVE_START_TIME, db.SAVE_PICTURE) 
  else:
    db.add_new_log(id, status, pv, sv, db.DONT_SAVE_START_TIME, db.DONT_SAVE_PICTURE) 

  