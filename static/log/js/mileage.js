// $(document).ready(function() {
//     $("#7_mileage").hide();
//     $("#date_range").hide();
// });
//
// $(document).ready(function() {
//   $("#two").click(function(){
//     $("#all_mileage_graph").show('slow');
//     $("#7_mileage").hide('slow');
//     $("#date_ranges").hide('slow');
//   });
// });
//
// $(document).ready(function() {
//   $("#one").click(function(){
//     $("#7_mileage").show('slow');
//     $("#all_mileage_graph").hide('slow');
//     $("#date_ranges").hide('slow');
//   });
// });
//
// $(document).ready(function() {
//   $("#three").click(function(){
//     $("#date_ranges").show('slow');
//     $("#7_mileage").hide('slow');
//     $("#all_mileage_graph").hide('slow');
//   });
// });


// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart']});


// Draw the bar chart for the Anthony's pizza when Charts is loaded.
google.charts.setOnLoadCallback(drawYearChart);

// Callback that creates and populates a data table,
// instantiates the pie chart, passes in the data and
// draws it.
function drawYearChart() {

  // Create the data table.
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Day');
  data.addColumn('number', 'Miles');
  data.addRows(year_graph_data);

  // Set chart options
  var options = {'title':'Mileage',
                 'height':300,
                 'width':1200,
                 'trendlines': { 0: {} }
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('all_mileage_graph'));
  chart.draw(data, options);
}

// Draw the bar chart for Sarah's pizza when Charts is loaded.
google.charts.setOnLoadCallback(drawMonthChart);

function drawMonthChart() {

  // Create the data table.
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Day');
  data.addColumn('number', 'Miles');
  data.addRows(month_graph_data);

  // Set chart options
  var options = {'title':'Mileage',
                 'height':300,
                 'width':1000,
                 'trendlines': { 0: {} }
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('7_mileage'));
  chart.draw(data, options);
}

// Draw the bar chart for Sarah's pizza when Charts is loaded.
google.charts.setOnLoadCallback(drawWeekChart);

function drawWeekChart() {

  // Create the data table.
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Day');
  data.addColumn('number', 'Miles');
  data.addRows(week_graph_data);

  // Set chart options
  var options = {'title':'Mileage',
                 'height':300,
                 'width':1000
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('date_range'));
  chart.draw(data, options);
}
