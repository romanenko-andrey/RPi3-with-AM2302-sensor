import TK4S_RS485_LIB as RS485
import time
import ini_parser as ini

speed = float(ini.ReadSection('StageTwo')['ramp'])
print "speed = ", speed, " C/m"

start_temp = RS485.read_PV()
while type(start_temp) is str:
  print "try to take current temperature again..."
  start_temp = RS485.read_PV()

  
start_time = time.time()
print "Start time = ", time.strftime("%H:%M:%S")
print "Start temp = ", start_temp
    
while True:
  current_time = time.time()
  next_SV = (current_time - start_time) * speed / 60
  next_SV += start_temp
  RS485.write_SV(next_SV)
  time.sleep(0.05)
  pv = RS485.read_PV()
  print "next SV = ", int(next_SV), '; PV = ', pv
  time.sleep(1)

