import sqlite3
import sys
import time
import os.path
from os import listdir, getcwd
import TK4S_RS485_LIB as RS485
import subprocess

DB_FILENAME = '/var/www/lab_app/analysis.db'

def create_or_open_database():
  db_is_new = not os.path.exists(DB_FILENAME)
  conn = sqlite3.connect(DB_FILENAME)
  if db_is_new:
    print 'Creating schema LOGDATA'
    sql = '''create table if not exists LOGDATA(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_name TEXT, 
    rDatetime DATETIME,
    SV INT, PV INT,
    IMGNAME TEXT,
    COMMENTS TEXT);'''
    conn.execute(sql) # shortcut for conn.cursor().execute(sql)
    
    print 'Creating schema RESULTS'
    sql = '''create table if not exists RESULTS(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    LAB_NUMBER TEXT, ASH_POSITION INT,
    START_TIME DATETIME,
    OPERATOR TEXT, COMMENTS TEXT,
    TEMP1 INT, IMG1 BLOB, IMGNAME1 TEXT,
    TEMP2 INT, IMG2 BLOB, IMGNAME2 TEXT,
    TEMP3 INT, IMG3 BLOB, IMGNAME3 TEXT,
    TEMP4 INT, IMG4 BLOB, IMGNAME4 TEXT);'''
    conn.execute(sql)
  return conn
  
def new_analysis(lab_number, operator, comments = ''):
  conn = create_or_open_database()
  curs = conn.cursor()
  sql = """INSERT INTO RESULTS 
    (START_TIME, LAB_NUMBER, ASH_POSITION, OPERATOR, COMMENTS)       
    VALUES (datetime(CURRENT_TIMESTAMP, 'localtime'),?, ?, ?, ?);"""
  curs.execute(sql, [lab_number, 1, operator, comments])
  curs.execute(sql, [lab_number, 2, operator, comments])
  curs.execute(sql, [lab_number, 3, operator, comments])
  
  conn.commit()
  conn.close()

def insert_picture(analysis_id, stage, picture_file):
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
    conn.execute(sql,[atemp, sqlite3.Binary(ablob), picture_file, analysis_id]) 
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

  fname, fext = os.path.splitext( os.path.abspath(afile) )
  filename = fname + '_' + str(stage) + fext

  with open(filename, 'wb') as output_file:
    output_file.write(ablob)
  return filename       

def add_new_log(analysis_name, save_picture = True, comments = ''):
  pv = RS485.reads_PV()
  if type(pv) is str:
    return pv
    
  sv = RS485.reads_SV()
  if type(sv) is str:
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
    (analysis_name, rDatetime, SV, PV, IMGNAME, COMMENTS)       
    VALUES (?, datetime(CURRENT_TIMESTAMP, 'localtime'),?, ?, ?, ?);"""
  curs.execute(sql, [analysis_name, sv, pv, img_name, comments])
  conn.commit()
  conn.close()
