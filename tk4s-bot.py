import datetime as dt
import work_with_db as db
import ConfigParser
import TK4S_RS485_LIB as RS485
from time import sleep 
from math import ceil
import time
import sys
import RPi.GPIO as GPIO
import preheat

Config = ConfigParser.ConfigParser()
Config.read("/var/www/lab_app/settings.ini")

temp_interval = Config.getint('General', 'update_temp_interval')
log_interval = Config.getint('General', 'log_interval')
log_interval = ceil( log_interval / temp_interval )
max_temp = Config.getint('StageTwo', 'max_temp')
heat_ramp = Config.getint('StageTwo', 'heat_ramp')
cool_ramp = Config.getint('StageThree', 'cool_ramp')
min_temp = Config.getint('StageThree', 'min_temp')
start_photo_temp = Config.getint('StageTwo', 'start_photo_temp')

EXIT_PIN = 29
LED_PIN = 32

if (len(sys.argv) >= 2):
  try:
    start_photo_temp = int( sys.argv[1] )
  except:
	  start_photo_temp = 900

print '!!!!!!!!!!!!! START TK4S_BOT !!!!!!!!!!!!!'
print "temp_interval=", temp_interval, " max_temp=", max_temp, " min_temp=" , min_temp
print "log_interval=", log_interval*temp_interval, "cool_ramp=", cool_ramp, " heat_ramp=", heat_ramp
  
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(EXIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)
  
i = log_interval  
while True:
  i -= 1
   
  id, status, current_temp, start_time_str, start_temp = db.get_last_log()
  nextSV = current_temp
  
  if current_temp > max_temp: #COOLING START
    status = "COOLING"
    db.add_new_log_to_and("COOLING", 
                          db.SAVE_START_TIME, 
                          db.DONT_SAVE_PICTURE, 
                          current_temp, current_temp, 
                          "stop heating")
   
  if status == "STOP" or status == "PREHEAT" or not GPIO.input(EXIT_PIN):
    print '!!!!!!!!!!!!! STOP TK4S_BOT !!!!!!!!!!!!!!!!'
    GPIO.cleanup([EXIT_PIN, LED_PIN])
    exit()
    
  current_time = dt.datetime.now()
  start_time = dt.datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
  
  if current_time <  start_time:
    print '!!!!! ERROR TIME !!!!!!!! STOP TK4S_BOT !!!!!!!!!!!!!!!!'
    GPIO.cleanup([EXIT_PIN, LED_PIN])
    exit()
    
  if status == "HEATING":
    deltaT = (current_time - start_time).seconds * heat_ramp / 60
    nextSV = start_temp + deltaT
    if nextSV > 1600:
      nextSV = 1600
  elif status == "COOLING":
    try:
      deltaT = (current_time - start_time).seconds * cool_ramp / 60
      nextSV = start_temp - deltaT 
      if nextSV < min_temp:
        preheat.set_preheat_temp()
        print "TK4S_BOT was stopped after finishing the cooling process"
    except:
      print 'error in coolling process'
    if nextSV < min_temp:
      GPIO.cleanup([EXIT_PIN, LED_PIN])
      exit() 
      
  print status, "PV =", current_temp, "SV = ", nextSV, "time=", time.strftime('%Y-%m-%d %H:%M:%S'), "start_time=", start_time
  try:
    nextSV = int(nextSV)
    RS485.writes_SV(nextSV) 
  except:
    print "error int value SV ", nextSV
  
  
  if i == 0:
    i = log_interval
    pv = RS485.reads_PV()
    sv = RS485.reads_SV()
    if type(pv) is str:
      pv = current_temp
    if type(sv) is str:
      sv = nextSV
    print "write LOG to disk ...."
    if current_temp > start_photo_temp:
      GPIO.output(LED_PIN, GPIO.HIGH) 
      db.add_new_log(id, status, pv, sv, db.DONT_SAVE_START_TIME, db.SAVE_PICTURE) 
      GPIO.output(LED_PIN, GPIO.LOW) 
    else:
      db.add_new_log(id, status, pv, sv, db.DONT_SAVE_START_TIME, db.DONT_SAVE_PICTURE) 

  sleep(temp_interval)