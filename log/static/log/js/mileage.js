// Show Year graph, hide others
$(document).ready(function() {
  $(".graph_option").hover(function(){
    console.log("hey there");
    // $("#current_year_selector").css("background-color","blue");
  });
});

// -------------------- Mileage graph divs -----------------------
$(document).ready(function() {
    $("#week_mileage_graph").hide();
    $("#year_mileage_graph").hide();
    $("#date_range_graph").hide();
});

// Show Year graph, hide others
$(document).ready(function() {
  $("#current_year_selector").click(function(){
    $("#year_mileage_graph").show('slow');
    $("#month_mileage_graph").hide('slow');
    $("#week_mileage_graph").hide('slow');
    $("#date_range_graph").hide('slow');
  });
});

// Show Month Graph, hide others
$(document).ready(function() {
  $("#current_month_selector").click(function(){
    $("#year_mileage_graph").hide('slow');
    $("#month_mileage_graph").show('slow');
    $("#week_mileage_graph").hide('slow');
    $("#date_range_graph").hide('slow');
  });
});

// Show Week Graph, hide others
$(document).ready(function() {
  $("#current_week_selector").click(function(){
    $("#year_mileage_graph").hide('slow');
    $("#month_mileage_graph").hide('slow');
    $("#week_mileage_graph").show('slow');
    $("#date_rangegraph").hide('slow');
  });
});

$(document).ready(function() {
  $("#range_selector").click(function(){
    $("#year_mileage_graph").hide('slow');
    $("#month_mileage_graph").hide('slow');
    $("#week_mileage_graph").hide('slow');
    $("#date_range_graph").show('slow');
  });
});


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
  var options = {'title':'Current Year Mileage',
                 'height':300,
                 'width':850,
                //  'trendlines': { 0: {} }
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('year_mileage_graph'));
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
  var options = {'title':'Current Month Mileage',
                 'height':300,
                 'width':'100%',
                //  'trendlines': { 0: {} }
              };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('month_mileage_graph'));
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
  var options = {'title':'Current Week Mileage',
                 'height':300,
                 'width':850
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('week_mileage_graph'));
  chart.draw(data, options);
}

// Draw the bar chart for Sarah's pizza when Charts is loaded.
google.charts.setOnLoadCallback(drawRangeChart);

function drawWeekChart() {

  // Create the data table.
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Day');
  data.addColumn('number', 'Miles');
  data.addRows(range_graph_data);

  // Set chart options
  var options = {'title':'Date Range Graph',
                 'height':300,
                 'width':850,
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('date_range_graph'));
  chart.draw(data, options);
}
