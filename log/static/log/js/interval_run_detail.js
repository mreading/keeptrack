// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart']});

// Draw the bar chart for the Anthony's pizza when Charts is loaded.
google.charts.setOnLoadCallback(drawIntervalChart);

// Callback that creates and populates a data table,
// instantiates the pie chart, passes in the data and
// draws it.
function drawIntervalChart() {

  // Create the data table.
    var data = google.visualization.arrayToDataTable(interval_graph_data);
        
    var graphWidth = $('#interval_graph').parent().width()
        
    // Set chart options
    var options = {'title':'Interval Graph',
             'height':300,
             'width': graphWidth,
             legend:{position:'none'},
            };

    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.ColumnChart(document.getElementById('interval_graph'));
    chart.draw(data, options);
    
    //create trigger to resizeEnd event
    $(window).resize(function() {
        if(this.resizeTO) clearTimeout(this.resizeTO);
        this.resizeTO = setTimeout(function() {
            $(this).trigger('resizeEnd');
        }, 0);
    });

    //redraw graph when window resize is completed
    $(window).on('resizeEnd', function() {
        options['width'] = $('#interval_graph').parent().width();
        chart.draw(data, options);
    });
}
