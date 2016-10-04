
// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart']});

// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(drawChart);

// Callback that creates and populates a data table,
// instantiates the pie chart, passes in the data and
// draws it.
function drawChart() {

  // Create the data table.
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Day');
  data.addColumn('number', 'Miles');
  data.addRows([
    ['Monday', 13],
    ['Tuesday', 7],
    ['Wednesday', 7],
    ['Thursday', 9],
    ['Friday', 5],
    ['Saturday', 8],
    ['Sunday', 0]
  ]);

  // Set chart options
  var options = {'title':'Mileage',
                 'width':600,
                 'height':300};

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
  chart.draw(data, options);
}
