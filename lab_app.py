from flask import Flask, request, render_template, redirect
import time
import datetime
import arrow
import work_with_db as db

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
  try: 
    analysis_id = int(analysis_id)
  except:
    print "id not a number"
    return redirect('/')
    
  print "id = ", analysis_id  
    
  log = db.get_log(analysis_id)
  return render_template("analysis.html", analysis_id = analysis_id, log = log)

  
@app.route("/new_test", methods=['POST']) 
def new_test():
  lab_number1  = request.form.get('lab_number1','') 
  lab_number2  = request.form.get('lab_number2','')
  lab_number3  = request.form.get('lab_number3','')
  comments1    = request.form.get('comments1','') 
  comments2    = request.form.get('comments2','')
  comments3    = request.form.get('comments3','')
  operator_name = request.form.get('operator','')

  print "ANALYSIS REQUEST:"
  print request.form
  analysis_id = db.new_analysis([lab_number1, lab_number2, lab_number3], 
                       operator_name, [comments1, comments2, comments3])
  
  #return render_template("analysis.html", analysis_id = analysis_id)
  #return redirect( url_for('/analysis') )
  return redirect( "/analysis?id=%s" % analysis_id )

                        
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
    id = results[0][1]
  else:
    results = db.get_results_for_dates(from_date_str, to_date_str)
   
  return [results, id, from_date_str, to_date_str]          
 
    
    
def validate_date(d):
  try:
    datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
    return True
  except ValueError:
    return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
