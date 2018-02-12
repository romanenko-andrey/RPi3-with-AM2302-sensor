import subprocess
import time
from time import sleep
import ini_parser as ini
import TK4S_RS485_LIB as RS485

speed = float(ini.ReadSection('StageTwo')['ramp'])

start_temp = RS485.read_PV()
while type(start_temp) is str:
  print "try to take current temperature again..."
  start_temp = RS485.read_PV()

start_time = time.time()
print "Start time = ", time.strftime("%H:%M:%S")
print "Start temp = ", start_temp

def update_PV(startPV, speedSV, next_time):
  current_time = time.time()
  next_SV = (current_time - next_time) * speedSV / 60
  next_SV += startPV
  RS485.write_SV(next_SV)


while True:
  y=(0.5)
  subprocess.Popen(["python", '/var/www/lab_app/read_and_save_db.py', 'test_name'])
  subprocess.Popen(["python", '/var/www/lab_app/test/1.py'])
  sleep(y)
  subprocess.Popen(["python", '/var/www/lab_app/test/2.py', str(start_time)])
  sleep(y)
  subprocess.Popen(["python", '/var/www/lab_app/test/3.py'])
  sleep(y)
  subprocess.Popen(["python", '/var/www/lab_app/test/4.py'])
  sleep(y)