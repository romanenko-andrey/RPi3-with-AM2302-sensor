
from flask import Flask, request, render_template

import time
import datetime

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
		return render_template("lab_temp.html",temp=temperature,hum=humidity)
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

@app.route("/lab_env_db")
def lab_env_db():
	import sqlite3
	conn = sqlite3.connect('/var/www/lab_app/lab_app.db')
	curs = conn.cursor()
	curs.execute("SELECT * FROM temperatures")
	temperatures = curs.fetchall()
	curs.execute("SELECT * FROM humidities")
	humidities = curs.fetchall()
	conn.close()
	return render_template("lab_env_db.html",temp=temperatures,hum=humidities)

@app.route("/lab_env_db2", methods=['GET']) 
def lab_env_db2():
        temperatures, humidities, from_date_str, to_date_str = get_records()
	return render_template("lab_env_db.html",temp = temperatures, hum = humidities)

def get_records():
        from_date_str 	= request.args.get('from',time.strftime("%Y-%m-%d %H:%M")) #Get the from date value from the URL
 	to_date_str 	= request.args.get('to',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL

	print "from = " + from_date_str
        print "to = " + to_date_str

        if not validate_date(from_date_str):		 			   # Validate date before sending it to the DB
		from_date_str 	= time.strftime("%Y-%m-%d 00:00")
	if not validate_date(to_date_str):
 		to_date_str 	= time.strftime("%Y-%m-%d %H:%M")		   # Validate date before sending it to the DB

        print "from2 = " + from_date_str
        print "to2 = " + to_date_str	

	import sqlite3
	conn = sqlite3.connect('/var/www/lab_app/lab_app.db')
	curs = conn.cursor()
	curs.execute("SELECT * FROM temperatures WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
	temperatures = curs.fetchall()
	curs.execute("SELECT * FROM humidities WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
	humidities = curs.fetchall()
	conn.close()
        return [temperatures, humidities, from_date_str, to_date_str]

def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
