import subprocess
import time
from time import sleep

start_time = time.time()
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