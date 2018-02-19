import work_with_db as db
import time
import subprocess

#db.insert_picture(6, 3, 'static/images/2018-02-12/11:24:45+114.jpg')
#db.extract_picture(6,3)
print db.add_new_log('The NEW', True, 'hi');

#while True:
#  cmd = "raspistill -w 720 -h 720 -t 100 -vf -hf -o static/images/test.jpg"
#  subprocess.call(cmd, shell=True)
#  time.sleep(2)
#  print time.strftime("%Y-%m-%d %H:%M:%S") + 'Ok'
  
