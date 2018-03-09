import sqlite3
import sys
import time
import datetime as dt
import os.path
from os import listdir, getcwd
import TK4S_RS485_LIB as RS485
import subprocess
import ConfigParser
import RPi.GPIO as GPIO
import work_with_camera

Config = ConfigParser.ConfigParser()
Config.read("/var/www/lab_app/settings.ini")
try:
  log_per_page = Config.getint('General', 'log_per_page')
except:
  log_per_page = 30

print "log_per_page = ", log_per_page

DB_FILENAME = '/var/www/lab_app/analysis.db'
LED_PIN = 32
SAVE_PICTURE = True
DONT_SAVE_PICTURE = False
SAVE_START_TIME = True
DONT_SAVE_START_TIME = False

def create_or_open_database():
  db_is_new = not os.path.exists(DB_FILENAME)
  conn = sqlite3.connect(DB_FILENAME)
  if db_is_new:
    print 'Creating schema LOGDATA'
    sql = '''create table if not exists LOGDATA(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ANALYSIS_ID INTEGER, 
    rDatetime DATETIME,
    SV INTEGER, 
    PV INTEGER,
    IMGNAME TEXT,
    START_TEMP INTEGER,
    START_TIME DATETIME,
    STATUS TEXT,
    COMMENTS TEXT);'''
    conn.execute(sql) # shortcut for conn.cursor().execute(sql)
    
    print 'Creating schema RESULTS'
    sql = '''create table if not exists RESULTS(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ANALYSIS_ID INTEGER, 
    rDatetime DATETIME,
    LAB_NUMBER TEXT, ASH_POSITION INTEGER,
    OPERATOR TEXT, COMMENTS TEXT,
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
    (rDatetime, ANALYSIS_ID, LAB_NUMBER, ASH_POSITION, OPERATOR, COMMENTS)       
    VALUES (?, ? ,?, ?, ?, ?);"""
    
  curs.execute(sql, [rDatetime, analysis_id, lab_numbers[0], 1, operator, comments[0]])
  curs.execute(sql, [rDatetime, analysis_id, lab_numbers[1], 2, operator, comments[1]])
  curs.execute(sql, [rDatetime, analysis_id, lab_numbers[2], 3, operator, comments[2]])
  
  conn.commit()
  conn.close()
  add_new_log(analysis_id, "READY", SAVE_START_TIME, DONT_SAVE_PICTURE, "initial log")
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

def add_new_log_to_and(status, save_start_position, save_picture, comments = ''):
  id, status_now, temp, start_temp, start_time  = get_last_log()
  add_new_log(id, status, save_start_position, save_picture, comments)
    
def add_new_log(analysis_id, status, save_start_position = False, save_picture = True, comments = ''):
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(LED_PIN, GPIO.OUT)
  GPIO.output(LED_PIN, GPIO.HIGH)
  
  pv, sv, img_name = get_temp_and_img(save_picture)
  
  conn = create_or_open_database()
  curs = conn.cursor()
  
  if save_start_position == True:
    #save new start time and start temp to log
    start_time = time.strftime('%Y-%m-%d %H:%M:%S')
    start_temp = pv 
  else:
    #take start time and start temp from last log
    curs.execute("SELECT START_TEMP, START_TIME FROM LOGDATA ORDER BY rDatetime DESC limit 1")
    start_temp, start_time = curs.fetchone() 
 
  print [analysis_id, sv, pv, img_name, comments, status, start_time, start_temp]

  sql = """INSERT INTO LOGDATA 
    (analysis_id, rDatetime, SV, PV, IMGNAME, COMMENTS, STATUS, START_TIME, START_TEMP)       
    VALUES (?, datetime(CURRENT_TIMESTAMP, 'localtime'),?, ?, ?, ?, ?, ?, ?);"""
  curs.execute(sql, [analysis_id, sv, pv, img_name, comments, status, start_time, start_temp])
  conn.commit()
  conn.close()
  
  GPIO.output(LED_PIN, GPIO.LOW)
  GPIO.cleanup()
  
  return [sv, pv, img_name]
  
def get_log(analysis_id, page=0):
  conn = create_or_open_database()
  curs = conn.cursor()
  sql = """SELECT * FROM LOGDATA WHERE ANALYSIS_ID = ? ORDER BY rDatetime DESC LIMIT ? OFFSET ?;"""
  try:
    p = int(page)
  except:
    p = 0
  curs.execute(sql, [analysis_id, log_per_page, p*log_per_page]) 
  res = curs.fetchall()
  conn.commit()
  conn.close()
  return res

def get_n_log(analysis_id, count_str):
  conn = create_or_open_database()
  curs = conn.cursor()
  sql = """SELECT * FROM LOGDATA WHERE ANALYSIS_ID = ? ORDER BY rDatetime DESC LIMIT ?;"""
  try:
    count = int(count_str)
  except:
    count = 0
    
  curs.execute(sql, [analysis_id, count]) 
  res = curs.fetchall()
  new_list = []
  delta = 5
  for i in range(len(res) - delta):
    t1 = dt.datetime.strptime(res[i][2], '%Y-%m-%d %H:%M:%S')
    t2 = dt.datetime.strptime(res[i + delta][2], '%Y-%m-%d %H:%M:%S')
    deltaTime = (t1 - t2).seconds
    try:
      deltaTemp = res[i][4] - res[i + delta][4]
      ramp = 60.0*deltaTemp/deltaTime
      deltaPVandSV = res[i][4] - res[i][3]
    except:
      deltaTemp = 0
      ramp = 0
      deltaPVandSV = 0
    new_list.append( [deltaTime, deltaTemp, ramp, deltaPVandSV] )
  conn.commit()
  conn.close()
  return [res, new_list]  
  
def get_last_log():
  conn = create_or_open_database()
  curs = conn.cursor()
  curs.execute("SELECT ANALYSIS_ID, STATUS, PV, START_TIME, START_TEMP FROM LOGDATA ORDER BY rDatetime DESC limit 1")
  id, status, pv, start_time, start_temp = curs.fetchone()
  conn.commit()
  conn.close()
  return [id, status, pv, start_time, start_temp]

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
  
def get_temp_and_img(save_picture):
  pv = RS485.reads_PV()
  while type(pv) is str:
    print "get_temp_and_img --- Try get PV again"
    pv = RS485.reads_PV()
    
  sv = RS485.reads_SV()
  while type(sv) is str:
    print "get_temp_and_img --- Try get SV again"
    sv = RS485.reads_SV()
   
  if save_picture:
    img_path_src = 'static/images/' + time.strftime("%Y-%m-%d") + '/'  
    root_path = "/var/www/lab_app/"
    try:
      os.mkdir(root_path + img_path_src)
    except OSError as e:
      err_msg = e.strerror #this is a normal error when the img_path already issue
    img_name_src = img_path_src + time.strftime("%H:%M:%S+") + str(pv) + '.jpg'
    print img_name_src
    print root_path + img_name_src
    work_with_camera.get_photo('360', '360', root_path + img_name_src)
  else:
    img_name_src = ''
  return [pv, sv, img_name_src]

