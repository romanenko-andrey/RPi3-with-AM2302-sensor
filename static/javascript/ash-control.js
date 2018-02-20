 $("#preheat").click(function(){
  $("#status_info").text("Sending data...");
  $.get("/preheat").done(showResults);
  return false; 
});
  
$("#stop_heater").click(function(){
  $("#status_info").text("Sending data...");
  $.get("/stop_heater").done(showResults);
  return false; 
});

function showResults(data){
  var res = JSON.parse(data);
  $("#status_info").removeClass().addClass(res["state"])
  $("#status_info").text(res["msg"]);            
}
  
$("#new_test").click(function(){
  $("#new_test_form_section").toggle();
  return false; 
});

$("#search_test").click(function(){
  $("#search_form_section").toggle();
  return false; 
});

  
$("#update").click(function(){
  var id = $("#analysis_id").text();
  $("#status_info").text("Reading data of analysis #" + id + "...");
  $.get("/results?analysis_id=" + id).done( function (data){
    console.log(data);
    var res = JSON.parse(data);
    //$("#status_info").removeClass().addClass(res["state"])
    $("#status_info").text(data);  
  });
  return false; 
});