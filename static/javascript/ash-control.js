 $("#preheat").click(function(){
  $("#status_info").text("Sending data...");
  $.get("/preheat").done(showResults);
  return false; 
})
  
$("#stop_heater_and_log").click(function(){
  $("#status_info").text("Sending data...");
  $.get("/stop_heater").done(showResults);
  return false; 
})

$("#stop_and_cool").click(function(){
  $("#status_info").text("Sending data...");
  $.get("/cool").done(showResults);
  return false; 
})



function showResults(data){
  var res = JSON.parse(data);
  console.log(data);
  $("#status_info").removeClass().addClass(res["state"])
  $("#status_info").text(res["msg"]);            
}
  
$("#new_test").click(function(){
  $("#new_test_form_section").toggleClass("d-none");
  return false; 
})

$("#cancel_button").click(function(){
  $("#new_test_form_section").toggleClass("d-none");
  return false; 
})

$("#search_test").click(function(){
  $("#search_form_section").toggleClass("d-none");
  return false; 
})

  
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
})

function row_click(id){
  window.location.href="/analysis?id=" + id + "&page=0";
}

$(".img_small").click(function(target){
  $( this ).toggleClass("img_small").toggleClass("img_big");
})