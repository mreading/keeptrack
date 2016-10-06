$(document).ready(function() {
    $("#7_mileage").hide();
    $("#date_range").hide();
});

$(document).ready(function() {
  $("#one").click(function(){
    $("#all_mileage_graph").show('slow');
    $("#7_mileage").hide('slow');
    $("#date_range").hide('slow');
  });
});

$(document).ready(function() {
  $("#two").click(function(){
    $("#7_mileage").show('slow');
    $("#all_mileage_graph").hide('slow');
    $("#date_range").hide('slow');
  });
});

$(document).ready(function() {
  $("#three").click(function(){
    $("#date_range").show('slow');
    $("#7_mileage").hide('slow');
    $("#all_mileage_graph").hide('slow');
  });
});


// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart']});


// Draw the bar chart for the Anthony's pizza when Charts is loaded.
google.charts.setOnLoadCallback(drawAllChart);

// Callback that creates and populates a data table,
// instantiates the pie chart, passes in the data and
// draws it.
function drawAllChart() {

  // Create the data table.
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Day');
  data.addColumn('number', 'Miles');
  data.addRows(mileage_data);

  // Set chart options
  var options = {'title':'Mileage',
                 'height':300,
                 'width':1200
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('all_mileage_graph'));
  chart.draw(data, options);
}

// Draw the bar chart for Sarah's pizza when Charts is loaded.
google.charts.setOnLoadCallback(draw7Chart);

function draw7Chart() {

  // Create the data table.
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Day');
  data.addColumn('number', 'Miles');
  data.addRows(last_7);

  // Set chart options
  var options = {'title':'Mileage',
                 'height':300,
                 'width':1000
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('7_mileage'));
  chart.draw(data, options);
}

// Draw the bar chart for Sarah's pizza when Charts is loaded.
google.charts.setOnLoadCallback(drawRangeChart);

function drawRangeChart() {

  // Create the data table.
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Day');
  data.addColumn('number', 'Miles');
  data.addRows(dr_data);

  // Set chart options
  var options = {'title':'Mileage',
                 'height':300,
                 'width':1000
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('date_range'));
  chart.draw(data, options);
}
