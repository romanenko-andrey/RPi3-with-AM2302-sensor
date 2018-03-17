from flask import Flask, request, render_template, redirect
import time
import datetime
import arrow
import work_with_db as db
import subprocess
import json
import work_with_camera

app = Flask(__name__)
app.debug = True # Make this False if you are no longer debugging


@app.route("/", methods=['GET']) 
def ash():
  results, analysis_id, from_date_str, to_date_str = get_records()
  return render_template("ash_fusion.html",
                        results       = results,
                        from_date     = from_date_str, 
                        to_date       = to_date_str,
                        res_items     = len(results),
                        analysis_id   = analysis_id)
 
                        
@app.route("/analysis", methods=['GET']) 
def analysis():
  analysis_id  = request.args.get('id', None) 
  page = request.args.get('page', '0')  
  try: 
    analysis_id = int(analysis_id)
  except:
    return redirect('/')
  log = db.get_log(analysis_id, page)
  return render_template("analysis.html", analysis_id=analysis_id, log=log, page=page)

  
@app.route("/table", methods=['GET']) 
def table():
  analysis_id  = request.args.get('id', None) 
  count = request.args.get('count', '100')  
  print 'count', count
  try: 
    analysis_id = int(analysis_id)
  except:
    return redirect('/')
  log, ramp = db.get_n_log(analysis_id, count)
  return render_template("table.html", analysis_id=analysis_id, log=log, ramp=ramp, count=int(count) )

  
@app.route("/new_test", methods=['POST']) 
def new_test():
  ln1, ln2, ln3, c1, c2, c3, operator = get_records_for_new_analysis()
  analysis_id = db.new_analysis([ln1, ln2, ln3], operator, [c1, c2, c3])
  return redirect( "/analysis?id=%s" % analysis_id )

  
@app.route("/camera", methods=['GET'])  
def camera_get():    
  size = request.args.get('size','320x320')
  auto = request.args.get('auto','off')  
  win = request.args.get('win','block')
  w, h = size.split('x')
  img_name_src = 'static/images/camera' + size + '.jpg'
  img_name = '/var/www/lab_app/' + img_name_src
  if (win == 'block'):
    X0, Y0, dX, dY, pW, pH, sh, co, br, sa, awb, ex = work_with_camera.get_photo_area(img_name)
  else:
    X0, Y0, dX, dY, pW, pH, sh, co, br, sa, awb, ex = work_with_camera.get_photo(w, h, img_name)
  print request.args
  return render_template("img_test.html", img_name = img_name_src, auto = auto, win = win, 
                         x0=X0, y0=Y0, dx=dX, dY=dY, pW=pW, pH=pH, sh=sh, co=co, br=br, sa=sa, awb=awb, ex=ex)

@app.route("/camera", methods=['POST'])  
def camera_post():    
  x0 = request.form.get('x0', None)
  y0 = request.form.get('y0', None)
  dX = request.form.get('dX', None)
  dY = request.form.get('dY', None)
  sh = request.form.get('sh', None)  
  co = request.form.get('co', None)
  br = request.form.get('br', None)
  sa = request.form.get('sa', None)
  awb = request.form.get('awb', None)
  ex = request.form.get('ex', None)
  #print [x0, y0, dX, dY, sh, co, br, sa, awb, ex, default]
  default = request.form.get('default', 'False')
  if default == 'True':
    work_with_camera.loadDefault()
  else:
    work_with_camera.saveSettings(x0, y0, dX, dY, sh, co, br, sa, awb, ex)
  return redirect( "/camera" )
  
@app.route("/preheat", methods=['GET'])  #This method will start TK4 for heating on start temperature
def preheat():    
  import preheat
  return json.dumps( preheat.set_preheat_temp() )

  
@app.route("/stop_heater", methods=['GET'])  #This method will send SP=0 to TK4
def stop_heater():    
  import stop_heater
  return json.dumps( stop_heater.stop_heater() )

  
@app.route("/start", methods=['GET'])  #Start log-bot and heat-bot
def start_analysis():  
  import heating
  return json.dumps( heating.heating() )

  
@app.route("/cool", methods=['GET'])  #Start cooling-bot
def start_cooling():   
  import cooling
  return json.dumps( cooling.cooling() )

  
@app.route("/results", methods=['GET'])  #This method will send SP=0 to TK4
def get_results():    
  import json
  analysis_no = request.args.get('analysis_id', '0')
  res = db.get_log(analysis_no)
  return json.dumps(res)

  
def get_records():
  #Get the from date value from the URL
  from_date_str = request.args.get('from',time.strftime("%Y-%m-%d 00:00")) 
  to_date_str = request.args.get('to',time.strftime("%Y-%m-%d %H:%M"))   
  dates_req = request.args.get('from', None)
  id = None
  id_str = request.args.get('id', '')
  
  print "REQUEST:", request.args
  
  try: 
    id = int(id_str)
  except:
    print "id not a number"
   
  if not validate_date(from_date_str):
    from_date_str = time.strftime("%Y-%m-%d 00:00")
  if not validate_date(to_date_str):
    to_date_str = time.strftime("%Y-%m-%d %H:%M")
  
  if id != None:
    results = db.get_result_for_id(id)
  elif dates_req == None:
    results = db.get_last_result()
    if len(results) > 0:    
      id = results[0][1]
  else:
    results = db.get_results_for_dates(from_date_str, to_date_str)
   
  return [results, id, from_date_str, to_date_str]          

def get_records_for_new_analysis():
  l1 = request.form.get('lab_number1','') 
  l2 = request.form.get('lab_number2','')
  l3 = request.form.get('lab_number3','')
  c1 = request.form.get('comments1','') 
  c2 = request.form.get('comments2','')
  c3 = request.form.get('comments3','')
  o  = request.form.get('operator','')
  return  [l1, l2, l3, c1, c2, c3, o] 
  
def validate_date(d):
  try:
    datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
    return True
  except ValueError:
    return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
