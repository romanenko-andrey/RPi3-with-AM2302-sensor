from flask import Flask, request, render_template
import time
import datetime
import arrow
import work_with_db as db

app = Flask(__name__)
app.debug = True # Make this False if you are no longer debugging

@app.route("/")
def hello():
  return "Hello World!"

@app.route("/lab_temp")
def lab_temp():
	import sys
	import Adafruit_DHT
	humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)
	if humidity is not None and temperature is not None:
		return render_template("lab_temp.html",
    temp = temperature,
    hum = humidity,
    img_name = "static/images/test.jpg")
	else:
		return render_template("no_sensor.html")

@app.route("/test", methods=['GET'])
def test():
  s1 = request.args.get('from',time.strftime("%Y-%m-%d 00:00")) #Get the from date value from the URL
  s2 = request.args.get('to',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL
  s3 = 'good'
  s4 = 'time'
  if not validate_date(s1):
    s3 = time.strftime("%Y-%m-%d 00:00")
  if not validate_date(s2):
    s4 = time.strftime("%Y-%m-%d %H:%M")
  return "from = " + s1 +"; to = " + s2 + ' ' + s3 + ' ' + s4

  
@app.route("/new_test", methods=['POST']) 
def new_test():
  lab_number1  = request.form.get('lab_number1','') 
  lab_number2  = request.form.get('lab_number2','')
  lab_number3  = request.form.get('lab_number3','')
  operator_name = request.form.get('operator','')
  comments = request.form.get('comments','')
  print "NEW ANALYSIS REQUEST:"
  print request.form
  analysis_id = db.new_analysis([lab_number1, lab_number2, lab_number3], 
                                     operator_name, comments)
  return render_template("new_analysis.html",
                        lab_number1   = lab_number1,
                        lab_number2   = lab_number2,
                        lab_number3   = lab_number3, 
                        operator_name = operator_name,
                        comments      = comments,
                        analysis_id   = analysis_id)

                        
@app.route("/ash", methods=['GET']) 
def ash():
  temperatures, humidities, timezone, from_date_str, to_date_str = get_records()

  # Create new record tables so that datetimes are adjusted back to the user browser's time zone.
  time_adjusted_temperatures = []
  time_adjusted_humidities   = []
  
  for record in temperatures:
    local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
    time_adjusted_temperatures.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(record[2],2)])

  for record in humidities:
    local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
    time_adjusted_humidities.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(record[2],2)])

  print "rendering ash_fusion.html with: %s, %s, %s" % (timezone, from_date_str, to_date_str)

  return render_template("ash_fusion.html",
                        timezone      = timezone,
                        temp          = time_adjusted_temperatures,
                        hum           = time_adjusted_humidities, 
                        from_date     = from_date_str, 
                        to_date       = to_date_str,
                        temp_items    = len(temperatures),
                        hum_items     = len(humidities),
                        query_string  = request.query_string)

                        
@app.route("/lab_env_db", methods=['GET']) 
def lab_env_db():
  temperatures, humidities, timezone, from_date_str, to_date_str = get_records()

  # Create new record tables so that datetimes are adjusted back to the user browser's time zone.
  time_adjusted_temperatures = []
  time_adjusted_humidities   = []
  
  for record in temperatures:
    local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
    time_adjusted_temperatures.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(record[2],2)])

  for record in humidities:
    local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
    time_adjusted_humidities.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(record[2],2)])

  print "rendering lab_env_db.html with: %s, %s, %s" % (timezone, from_date_str, to_date_str)

  return render_template("lab_env_db.html",
                        timezone      = timezone,
                        temp          = time_adjusted_temperatures,
                        hum           = time_adjusted_humidities, 
                        from_date     = from_date_str, 
                        to_date       = to_date_str,
                        temp_items    = len(temperatures),
                        hum_items     = len(humidities),
                        query_string  = request.query_string) #This query string is used by the Plotly link

                        

@app.route("/preheat", methods=['GET'])  #This method will start TK4 for heating on start temperature
def preheat():    
  import json
  import preheat
  return json.dumps( preheat.set_preheat_temp() )

@app.route("/stop_heater", methods=['GET'])  #This method will send SP=0 to TK4
def stop_heater():    
  import json
  import stop_heater
  return json.dumps( stop_heater.stop_heater() )

@app.route("/results", methods=['GET'])  #This method will send SP=0 to TK4
def get_results():    
  import json
  analysis_no = request.args.get('analysis_id', '0')
  res = db.get_log(analysis_no)
  return json.dumps(res)
  
def get_records():
  import sqlite3
  from_date_str = request.args.get('from',time.strftime("%Y-%m-%d 00:00")) #Get the from date value from the URL
  to_date_str   = request.args.get('to',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL
  timezone      = request.args.get('timezone','Etc/UTC');
  range_h_form  = request.args.get('range_h','');  #This will return a string, if field range_h exists in the request
  range_h_int   = "nan"  #initialise this variable with not a number
  id_form       = request.args.get('id','');
  
  print "REQUEST:"
  print request.args

  try: 
    range_h_int = int(range_h_form)
  except:
    print "range_h not a number"
 
  try: 
    id = int(id)
  except:
    print "id not a number"
   
  if not validate_date(from_date_str):			# Validate date before sending it to the DB
    from_date_str = time.strftime("%Y-%m-%d 00:00")
  if not validate_date(to_date_str):
    to_date_str = time.strftime("%Y-%m-%d %H:%M")		# Validate date before sending it to the DB
  
  print 'Time recieve : From= %s, to= %s, timezone= %s' % (from_date_str, to_date_str, timezone)
  
  # Create datetime object so that we can convert to UTC from the browser's local time
  from_date_obj  = datetime.datetime.strptime(from_date_str,'%Y-%m-%d %H:%M')
  to_date_obj    = datetime.datetime.strptime(to_date_str,'%Y-%m-%d %H:%M')

  # If range_h is defined, we don't need the from and to times
  if isinstance(range_h_int,int):
    arrow_time_from = arrow.utcnow().replace(hours = -range_h_int)
    arrow_time_to   = arrow.utcnow()
    from_date_utc   = arrow_time_from.strftime("%Y-%m-%d %H:%M")
    to_date_utc     = arrow_time_to.strftime("%Y-%m-%d %H:%M")
    from_date_str   = arrow_time_from.to(timezone).strftime("%Y-%m-%d %H:%M")
    to_date_str     = arrow_time_to.to(timezone).strftime("%Y-%m-%d %H:%M")
  else:
    #Convert datetimes to UTC so we can retrieve the appropriate records from the database
    from_date_utc   = arrow.get(from_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")	
    to_date_utc     = arrow.get(to_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")

  conn = sqlite3.connect('/var/www/lab_app/lab_app.db')
  curs = conn.cursor()
  curs.execute("SELECT * FROM temperatures WHERE rDateTime BETWEEN ? AND ?", (from_date_utc.format('YYYY-MM-DD HH:mm'), to_date_utc.format('YYYY-MM-DD HH:mm')))
  temperatures = curs.fetchall()
  curs.execute("SELECT * FROM humidities WHERE rDateTime BETWEEN ? AND ?", (from_date_utc.format('YYYY-MM-DD HH:mm'), to_date_utc.format('YYYY-MM-DD HH:mm')))
  humidities = curs.fetchall()
  conn.close()
  return [temperatures, humidities, timezone, from_date_str, to_date_str]          
 
    
    
def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
