// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart']});


// Draw the bar chart for the Anthony's pizza when Charts is loaded.
google.charts.setOnLoadCallback(drawIntervalChart);

// Callback that creates and populates a data table,
// instantiates the pie chart, passes in the data and
// draws it.
function drawIntervalChart() {

  // Create the data table.
  var data = new google.visualization.DataTable();
  data.addColumn('number', 'Rep');
  data.addColumn('timeofday', 'duration');
  data.addRows(interval_graph_data);
  // data.addRows([
  //   // hour, minute second millisecond
  //   [1, [20, 45, 0, 0]]
  // ])

  // Set chart options
  var options = {'title':'Interval Graph',
                 'height':300,
                 'width':850,
                //  'trendlines': { 0: {} }
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('interval_graph'));
  chart.draw(data, options);
}
