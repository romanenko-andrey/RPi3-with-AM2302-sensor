import datetime as dt
import work_with_db as db
import ConfigParser
import TK4S_RS485_LIB as RS485
from time import sleep 
import time
import RPi.GPIO as GPIO
import preheat

Config = ConfigParser.ConfigParser()
Config.read("/var/www/lab_app/settings.ini")

log_interval = Config.getint('General', 'update_temp_interval')
max_temp = Config.getint('StageTwo', 'max_temp')
heat_ramp = Config.getint('StageTwo', 'heat_ramp')
cool_ramp = Config.getint('StageThree', 'cool_ramp')
min_temp = Config.getint('StageThree', 'min_temp')

print '!!!!!!!!!!!!! START TK4S_BOT !!!!!!!!!!!!!'
print "log_interval=", log_interval, " max_temp=", max_temp, " min_temp=" , min_temp
print "cool_ramp=", cool_ramp, " heat_ramp=", heat_ramp
  
while True:
  id, status, current_temp, start_time_str, start_temp = db.get_last_log()
  nextSV = current_temp
  
  if status == "STOP" or status == "PREHEAT"  :
    print '!!!!!!!!!!!!! STOP TK4S_BOT !!!!!!!!!!!!!!!!'
    break
    
  current_time = dt.datetime.now()
  start_time = dt.datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
  
  if current_time <  start_time:
    print '!!!!! ERROR TIME !!!!!!!! STOP TK4S_BOT !!!!!!!!!!!!!!!!'
    break
    
  if status == "HEATING":
    deltaT = (current_time - start_time).seconds * heat_ramp / 60
    nextSV = start_temp + deltaT
    if current_temp > max_temp:
      #COOLING START
      db.add_new_log_to_and("COOLING", db.SAVE_START_TIME, db.DONT_SAVE_PICTURE, "stop heating")
  elif status == "COOLING":
    try:
      deltaT = (current_time - start_time).seconds * cool_ramp / 60
      nextSV = start_temp - deltaT 
      if nextSV < min_temp:
        #stop cooling and 
        #db.add_new_log_to_and("STOP", db.SAVE_START_TIME, db.DONT_SAVE_PICTURE, "stop heating")  
        preheat.set_preheat_temp()
        print "TK4S_BOT was stopped after finishing the cooling process"
        exit()       
    except:
      print 'error in coolling process'
       
  print status, "PV =", current_temp, "SV = ", nextSV, "time=", time.strftime('%Y-%m-%d %H:%M:%S'), "start_time=", start_time
  try:
    nextSV = int(nextSV)
    RS485.writes_SV(nextSV) 
  except:
    print "error int value SV ", nextSV
  
  sleep(log_interval)