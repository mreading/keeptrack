$(document).ready(function() {
   $('.btn').bind("mouseover", function(){
       var color = $(this).css("background-color");

       $(this).css("background", "#dcc7aa");

       $(this).bind("mouseout", function(){
           $(this).css("background", color);
       })
   })
})

// -------------------- Mileage graph divs -----------------------
$(document).ready(function() {
    console.log(show_range_graph_first);
    if (Boolean(show_range_graph_first)) {
      console.log("sup");
      $("#month_mileage_graph").hide();
      $("#week_mileage_graph").hide();
      $("#year_mileage_graph").hide();
    }
    else {
      console.log("blech");
      $("#week_mileage_graph").hide();
      $("#year_mileage_graph").hide();
      $("#date_range_graph").hide();
    }
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
    $("#date_range_graph").hide('slow');
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

//-----------------------------------------------------------------------------
function drawYearChart() {

  // Create the data table.
  var data = google.visualization.arrayToDataTable(year_graph_data);
  var view = new google.visualization.DataView(data);
  view.setColumns([0, 1, 2])

  // Set chart options
  var options = {'title':'Current Year Mileage',
                 'height':300,
                'width':"100%",
                 legend:{position:'none'}
                //  'trendlines': { 0: {} }
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('year_mileage_graph'));
  chart.draw(view, options);

  var selectHandler = function(e) {
    window.location = data.getValue(chart.getSelection()[0]['row'], 3);
  }
  google.visualization.events.addListener(chart, 'select', selectHandler);
}

//-----------------------------------------------------------------------------
google.charts.setOnLoadCallback(drawMonthChart);

function drawMonthChart() {

  // Create the data table.
  var data = google.visualization.arrayToDataTable(month_graph_data);
  var view = new google.visualization.DataView(data);
  view.setColumns([0, 1, 2])

  // Set chart options
  var options = {'title':'Current Month Mileage',
                 'height':300,
                 'width':"100%",
                 legend:{position:'none'}
                //  'trendlines': { 0: {} }
              };

  // var selectHandler = function(e) {
  //   window.location = data.getValue(chart.getSelection()[0]['row'], 3);
  // }
  //  // Add our selection handler.
  //  google.visualization.events.addListener(chart, 'select', selectHandler);
  //   }

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('month_mileage_graph'));
  chart.draw(view, options);

  var selectHandler = function(e) {
    window.location = data.getValue(chart.getSelection()[0]['row'], 3);
  }
  google.visualization.events.addListener(chart, 'select', selectHandler);
}

//-----------------------------------------------------------------------------
google.charts.setOnLoadCallback(drawWeekChart);

function drawWeekChart() {

  // Create the data table.
  var data = google.visualization.arrayToDataTable(week_graph_data);
  var view = new google.visualization.DataView(data);
  view.setColumns([0, 1, 2])

  // Set chart options
  var options = {'title':'Current Week Mileage',
                 'height':300,
                 'width':"100%",
                 legend:{position:'none'},
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('week_mileage_graph'));
  chart.draw(view, options);

  var selectHandler = function(e) {
    window.location = data.getValue(chart.getSelection()[0]['row'], 3);
  }
  google.visualization.events.addListener(chart, 'select', selectHandler);
}

//-----------------------------------------------------------------------------
google.charts.setOnLoadCallback(drawRangeChart);

function drawRangeChart() {

  // Create the data table.
  var data = google.visualization.arrayToDataTable(range_graph_data);
  var view = new google.visualization.DataView(data);
  view.setColumns([0, 1, 2])

  // Set chart options
  var options = {'title':'Date Range Graph',
                 'height':300,
                 'width':"100%",
                 legend:{position:'none'}
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('date_range_graph'));
  chart.draw(view, options);

  var selectHandler = function(e) {
    window.location = data.getValue(chart.getSelection()[0]['row'], 3);
  }
  google.visualization.events.addListener(chart, 'select', selectHandler);
}
