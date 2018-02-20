import sqlite3
import sys
import time
import os.path
from os import listdir, getcwd
import TK4S_RS485_LIB as RS485
import subprocess


DB_FILENAME = '/var/www/lab_app/analysis.db'
LED_PIN = 32


def create_or_open_database():
  db_is_new = not os.path.exists(DB_FILENAME)
  conn = sqlite3.connect(DB_FILENAME)
  if db_is_new:
    print 'Creating schema LOGDATA'
    sql = '''create table if not exists LOGDATA(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ANALYSIS_ID INTEGER, 
    rDatetime DATETIME,
    SV INTEGER, PV INTEGER,
    IMGNAME TEXT,
    COMMENTS TEXT);'''
    conn.execute(sql) # shortcut for conn.cursor().execute(sql)
    
    print 'Creating schema RESULTS'
    sql = '''create table if not exists RESULTS(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ANALYSIS_ID INTEGER, 
    rDatetime DATETIME,
    LAB_NUMBER TEXT, ASH_POSITION INTEGER,
    OPERATOR TEXT, COMMENTS TEXT,
    START_TEMP INTEGER,
    START_TIME DATETIME,
    STATUS TEXT,
    TEMP1 INTEGER, IMG1 BLOB, IMGNAME1 TEXT,
    TEMP2 INTEGER, IMG2 BLOB, IMGNAME2 TEXT,
    TEMP3 INTEGER, IMG3 BLOB, IMGNAME3 TEXT,
    TEMP4 INTEGER, IMG4 BLOB, IMGNAME4 TEXT);'''
    conn.execute(sql)
  return conn


def test():
  conn = create_or_open_database()
  curs = conn.cursor()  
  sql = """SELECT analysis_id FROM LOGDATA ORDER BY rDatetime DESC limit 1;"""
  curs.execute(sql)
  s = curs.fetchone() 
  print 's=', s
  conn.close()
  return s
  
#db.new_analysis(['1','2','3'], 'roll', '')
#import work_with_db as db

  
def new_analysis(lab_numbers, operator, comments = ['', '', '']):
  conn = create_or_open_database()
  curs = conn.cursor()
  
  sql = """SELECT analysis_id FROM LOGDATA ORDER BY rDatetime DESC limit 1;"""
   
  curs.execute(sql)
  res = curs.fetchone()  
  if res == None:
    analysis_id = 1
  else:
    analysis_id = res[0] + 1
  print "new analysis number = ", analysis_id
  
  rDatetime = time.strftime('%Y-%m-%d %H:%M:%S')
  sql = """INSERT INTO RESULTS 
    (rDatetime, ANALYSIS_ID, LAB_NUMBER, ASH_POSITION, OPERATOR, COMMENTS, STATUS)       
    VALUES (?, ? ,?, ?, ?, ?, ?);"""
    
  status = "READY"
  curs.execute(sql, [rDatetime, analysis_id, lab_numbers[0], 1, operator, comments[0], status])
  curs.execute(sql, [rDatetime, analysis_id, lab_numbers[1], 2, operator, comments[1], status])
  curs.execute(sql, [rDatetime, analysis_id, lab_numbers[2], 3, operator, comments[2], status])
  
  conn.commit()
  conn.close()
  add_new_log(analysis_id, False, "initial log")
  return analysis_id

def insert_picture(id, stage, picture_file):
  if not os.path.exists(picture_file):
    print 'file name ', picture_file, ' is not correct'
    return False
  
  conn = create_or_open_database()
  
  with open(picture_file, 'rb') as input_file:
    ablob = input_file.read()
    base=os.path.basename(picture_file)
    afile, ext = os.path.splitext(base)
    atime, atemp = afile.split('+')

    #cutting pictures will be here soon :)
    sql='''UPDATE RESULTS SET TEMP1 = ?, IMG1 = ?, IMGNAME1 = ? WHERE ID=?;'''
    if stage == 2:
      sql='''UPDATE RESULTS SET TEMP2 = ?, IMG2 = ?, IMGNAME2 = ? WHERE ID=?;'''
    if stage == 3:
      sql='''UPDATE RESULTS SET TEMP3 = ?, IMG3 = ?, IMGNAME3 = ? WHERE ID=?;'''
    if stage == 4:
      sql='''UPDATE RESULTS SET TEMP4 = ?, IMG4 = ?, IMGNAME4 = ? WHERE ID=?;'''
    conn.execute(sql,[atemp, sqlite3.Binary(ablob), picture_file, id]) 
    conn.commit()
  conn.close()
  return True
  
def extract_picture(analysis_id, stage):
  conn = create_or_open_database()
  curs = conn.cursor()
  
  sql = "SELECT TEMP1, IMGNAME1, IMG1 FROM RESULTS WHERE id = :id"
  if stage == 2:
    sql = "SELECT TEMP2, IMGNAME2, IMG2 FROM RESULTS WHERE id = :id"
  if stage == 3:
    sql = "SELECT TEMP3, IMGNAME3, IMG3 FROM RESULTS WHERE id = :id"
  if stage == 4:
    sql = "SELECT TEMP4, IMGNAME4, IMG4 FROM RESULTS WHERE id = :id"
  
  param = {'id': analysis_id}
  curs.execute(sql, param)
  atemp, afile, ablob = curs.fetchone()
  conn.commit()
  conn.close()
  
  fname, fext = os.path.splitext( os.path.abspath(afile) )
  filename = fname + '_' + str(stage) + fext

  with open(filename, 'wb') as output_file:
    output_file.write(ablob)
  return filename       

  
def add_new_log(analysis_id, save_picture = True, comments = ''):
  import RPi.GPIO as GPIO
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(LED_PIN, GPIO.OUT)
  GPIO.output(LED_PIN, GPIO.HIGH)

  pv = RS485.reads_PV()
  if type(pv) is str:
    GPIO.cleanup()
    return pv
    
  sv = RS485.reads_SV()
  if type(sv) is str:
    GPIO.cleanup()
    return sv
   
  if save_picture:
    img_path = 'static/images/' + time.strftime("%Y-%m-%d") + '/'  
    try:
      os.mkdir(img_path)
    except OSError as e:
      err_msg = e.strerror #this is a normal error when the img_path already issue
    img_name = img_path + time.strftime("%H:%M:%S+") + str(pv) + '.jpg'
    cmd = "raspistill -w 720 -h 720 -t 100 -vf -hf -o " + img_name
    subprocess.call(cmd, shell=True)
  else:
    img_name = ''
  
  conn = create_or_open_database()
  curs = conn.cursor()
  sql = """INSERT INTO LOGDATA 
    (analysis_id, rDatetime, SV, PV, IMGNAME, COMMENTS)       
    VALUES (?, datetime(CURRENT_TIMESTAMP, 'localtime'),?, ?, ?, ?);"""
  curs.execute(sql, [analysis_id, sv, pv, img_name, comments])
  conn.commit()
  conn.close()
  GPIO.output(LED_PIN, GPIO.LOW)
  GPIO.cleanup()
  return [sv, pv, img_name]
  
def get_log(analysis_id):
  conn = create_or_open_database()
  curs = conn.cursor()
  sql = """SELECT rDatetime, SV, PV, IMGNAME, COMMENTS FROM LOGDATA WHERE ANALYSIS_ID = ?;"""
  curs.execute(sql, [analysis_id]) 
  res = curs.fetchall()
  conn.commit()
  conn.close()
  return res

def get_results_for_dates(date_from, date_to):
  conn = create_or_open_database()
  curs = conn.cursor()
  curs.execute("SELECT * FROM RESULTS WHERE rDateTime BETWEEN ? AND ?", [date_from, date_to])
  res = curs.fetchall()
  conn.close()
  return res
  
def get_result_for_id(id):
  conn = create_or_open_database()
  curs = conn.cursor()
  curs.execute("SELECT * FROM RESULTS WHERE ANALYSIS_ID = ?", [id])
  res = curs.fetchall()
  conn.close()
  return res

def get_last_result():
  conn = create_or_open_database()
  curs = conn.cursor()
  curs.execute("SELECT * FROM RESULTS ORDER BY ANALYSIS_ID DESC limit 3")
  res = curs.fetchall()
  conn.close()
  return res  

