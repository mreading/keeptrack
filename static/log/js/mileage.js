// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart']});

var range_index = 3;
$(document).ready(function() {
   $('.btn').bind("mouseover", function(){
       var color = $(this).css("background-color");

       $(this).css("background", "#dcc7aa");

       $(this).bind("mouseout", function(){
           $(this).css("background", color);
       })
   })

   // CODE NEEDED FOR FORM SAFETY
   function getCookie(name) {
        var cookieValue = null;
        var i = 0;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (i; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

   $("#range_form").submit(function(e) {
       //need some indication of loading
       $.ajax({
           type: "POST",
           data: $("#range_form").serialize(),
           url: "/log/ajax/range_select/",
           success: function(data) {
               range_graph_data = JSON.parse(data);
               graphSelector.setGraph(range_index);
            }
       });
       e.preventDefault();
   })
})


//#########################################################################################
class GraphOption {
  constructor(buttonID, graphID, data, drawFunc) {
    this.buttonID = buttonID;
    this.graphID = graphID;
    this.data = data;
    this.drawFunc = drawFunc;
  }
}

class GraphSelector {
    // graphList is a list of Graph objects
    // currentGraph takes the index of the default graph
    constructor(graphList, currentGraphIndex = 0) {
        this.graphList = graphList;
        this.currentGraphIndex = currentGraphIndex;

        var thisGraph = this
        google.charts.setOnLoadCallback(function() {
            $(document).ready(function() {
                thisGraph.initiateDefaultGraph();
            });
        });
    }

    getActiveDivWidth() {
        return document.getElementById(this.graphList[this.currentGraphIndex].graphID.slice(1)).offsetWidth
    }

    initiateDefaultGraph() {
        this.initiateButtons();

        // hide non-active graphs - should be done sooner!
        var numGraphs = this.graphList.length;
        for (var nthGraph = 0; nthGraph < numGraphs; nthGraph++) {
            if (this.currentGraphIndex != nthGraph) {
                var currentGraphID = this.graphList[nthGraph].graphID;
                $(currentGraphID).hide();
            }
        }

        // draw default
        this.graphList[this.currentGraphIndex].drawFunc();
    }

    initiateButtons() {
        var thisGraph = this;

        var numGraphs = this.graphList.length;
        function buttonCallback(index) {
            return function() {
                thisGraph.setGraph(index);
            }
        }

        for (var nthGraph = 0; nthGraph < numGraphs; nthGraph++) {
            var buttonID = this.graphList[nthGraph].buttonID;
            $(buttonID).click(buttonCallback(nthGraph));
        }

        this.setActiveButton(this.currentGraphIndex);
    }

    setActiveButton(index) {

        var buttonID = this.graphList[index].buttonID;
        $(buttonID).addClass('active');
    }

    setGraph(index) {
        if (this.currentGraphIndex != index) {
            var prevGraphID = this.graphList[this.currentGraphIndex].graphID;
            var prevButtonID = this.graphList[this.currentGraphIndex].buttonID;

            $(prevGraphID).hide('slow');
            var currentGraphID = this.graphList[index].graphID;
            $(currentGraphID).show('slow', this.graphList[index].drawFunc());

            this.currentGraphIndex = index;
            var currentButtonID = this.graphList[this.currentGraphIndex].buttonID;

            $(prevButtonID).removeClass('active');
            $(currentButtonID).addClass('active');
        }
        else if (index=range_index) {
            this.graphList[index].drawFunc();
        }
    }
}

// ADD ORDER HERE
var graphOptionData = [["#current_year_selector", "#year_mileage_graph", year_graph_data, drawYearChart], ["#current_month_selector", "#month_mileage_graph", month_graph_data, drawMonthChart], ["#current_week_selector", "#week_mileage_graph", week_graph_data, drawWeekChart], ["#range_selector", "#date_range_graph", range_graph_data, drawRangeChart]];

graphs = [];
numGraphs = graphOptionData.length
for (var nthGraph = 0; nthGraph < numGraphs; nthGraph++){
    graph = new GraphOption(graphOptionData[nthGraph][0], graphOptionData[nthGraph][1], graphOptionData[nthGraph][2], graphOptionData[nthGraph][3]);
    graphs.push(graph);
};

// Need to figure out how to change this based on the selected button - pass url variable?
var DEFAULT_GRAPH_INDEX = 1
graphSelector = new GraphSelector(graphs, DEFAULT_GRAPH_INDEX);
//#########################################################################################
//google.charts.setOnLoadCallback(drawYearChart);

//-----------------------------------------------------------------------------
function drawYearChart() {

    if (year_graph_data) {

  // Create the data table.
  var data = google.visualization.arrayToDataTable(year_graph_data);
  var view = new google.visualization.DataView(data);
  view.setColumns([0, 1, 2])

  var options = {'title':'Current Year Mileage',
                 'height':300,
                'width': graphSelector.getActiveDivWidth(),
                 'interpolateNulls': true,
                 'pointShape': 'circle',
                 'pointSize': 5,
                 'colors': ['#6b7a8f', '#f7c331'],
                 'legend':{position:'right'},
                 'isStacked':true
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('year_mileage_graph'));
  chart.draw(view, options);

  var selectHandler = function(e) {
    window.location = data.getValue(chart.getSelection()[0]['row'], 6);
  }
  google.visualization.events.addListener(chart, 'select', selectHandler);

    //create trigger to resizeEnd event
    $(window).resize(function() {
        if(this.resizeTO) clearTimeout(this.resizeTO);
        this.resizeTO = setTimeout(function() {
            $(this).trigger('resizeEnd');
        }, 0);
    });

    //redraw graph when window resize is completed
    $(window).on('resizeEnd', function() {
        options['width'] = graphSelector.getActiveDivWidth();
        chart.draw(view, options);
    });
    }

    else {
        $("#year_mileage_graph").html("<br><h4 class='error'>No Miles In This Date Range</h4><br>");
    }
}

// Default Graph to show (must account for date and other items being passed)
var LINK_INDEX = 6;

//-----------------------------------------------------------------------------
//google.charts.setOnLoadCallback(drawMonthChart);

function drawMonthChart() {

  if (month_graph_data) {

    // Create the data table.
    var data = google.visualization.arrayToDataTable(month_graph_data);
    var view = new google.visualization.DataView(data);
    view.setColumns([0, 1, 2, 4])

    // Set chart options
    var options = {'title':'Current Month Mileage',
                   'height':300,
                   'width':graphSelector.getActiveDivWidth(),
                   'interpolateNulls': true,
                   'pointShape': 'circle',
                   'pointSize': 5,
                   'colors': ['#6b7a8f', '#f7c331', '#f7882f'],
                   'legend':{position:'right'},
                   'isStacked':true
                };

    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.ColumnChart(document.getElementById('month_mileage_graph'));
    chart.draw(view, options);

    var selectHandler = function() {
        var row = chart.getSelection()[0]['row']
        // this means that we've selected a valid point
        if (row) {
            window.location = data.getValue(row, LINK_INDEX);
        }
    }
    google.visualization.events.addListener(chart, 'select', selectHandler);

    //create trigger to resizeEnd event
    $(window).resize(function() {
        if(this.resizeTO) clearTimeout(this.resizeTO);
        this.resizeTO = setTimeout(function() {
            $(this).trigger('resizeEnd');
        }, 0);
    });

    //redraw graph when window resize is completed
    $(window).on('resizeEnd', function() {
        options['width'] = graphSelector.getActiveDivWidth();
        chart.draw(view, options);
    });
  }
  else {
      $("#month_mileage_graph").html("<br><h4 class='error'>No Miles In This Date Range</h4><br>");
  }
}

//-----------------------------------------------------------------------------
//google.charts.setOnLoadCallback(drawWeekChart);

function drawWeekChart() {
    if (week_graph_data) {
      // Create the data table.
      var data = google.visualization.arrayToDataTable(week_graph_data);
      var view = new google.visualization.DataView(data);
      view.setColumns([0, 1, 2, 3, 4])

      // Set chart options
      var options = {'title':'Current Week Mileage',
                     'height':300,
                     'width':graphSelector.getActiveDivWidth(),
                     'interpolateNulls': true,
                     'pointShape': 'circle',
                     'pointSize': 5,
                     'colors': ['#6b7a8f', '#f7c331', '#dcc7aa', '#f7882f'],
                     'isStacked':true
                   };

      // Instantiate and draw our chart, passing in some options.
      var chart = new google.visualization.ColumnChart(document.getElementById('week_mileage_graph'));
      chart.draw(view, options);

      var selectHandler = function(e) {
        window.location = data.getValue(chart.getSelection()[0]['row'], LINK_INDEX);
      }
      google.visualization.events.addListener(chart, 'select', selectHandler);

        //create trigger to resizeEnd event
        $(window).resize(function() {
            if(this.resizeTO) clearTimeout(this.resizeTO);
            this.resizeTO = setTimeout(function() {
                $(this).trigger('resizeEnd');
            }, 0);
        });

        //redraw graph when window resize is completed
        $(window).on('resizeEnd', function() {
            options['width'] = graphSelector.getActiveDivWidth();
            chart.draw(view, options);
        });
        }
    else {
        $("#week_mileage_graph").html("<br><h4 class='error'>No Miles In This Date Range</h4><br>");
    }
}


//-----------------------------------------------------------------------------
//google.charts.setOnLoadCallback(drawRangeChart);

function drawRangeChart() {
    if (range_graph_data) {
      // Create the data table.
      var data = google.visualization.arrayToDataTable(range_graph_data);
      var view = new google.visualization.DataView(data);
      view.setColumns([0, 1, 2, 4])

      // Set chart options
      var options = {'title':'Date Range Graph',
                     'height':300,
                     'width':graphSelector.getActiveDivWidth(),
                     'interpolateNulls': true,
                     'pointShape': 'circle',
                     'pointSize': 5,
                     'colors': ['#6b7a8f', '#f7c331','#f7882f'],
                     'legend':{position:'right'},
                     'isStacked':true
                   };

      // Instantiate and draw our chart, passing in some options.
      var chart = new google.visualization.ColumnChart(document.getElementById('date_range_graph'));
      chart.draw(view, options);

      var selectHandler = function(e) {
        window.location = data.getValue(chart.getSelection()[0]['row'], LINK_INDEX);
      }
      google.visualization.events.addListener(chart, 'select', selectHandler);

        //create trigger to resizeEnd event
        $(window).resize(function() {
            if(this.resizeTO) clearTimeout(this.resizeTO);
            this.resizeTO = setTimeout(function() {
                $(this).trigger('resizeEnd');
            }, 0);
        });

        //redraw graph when window resize is completed
        $(window).on('resizeEnd', function() {
            options['width'] = graphSelector.getActiveDivWidth();
            chart.draw(view, options);
        });
        }
    else {
        $("#date_range_graph").html("<br><h4 class='error'>No Miles In This Date Range</h4><br>");
    }
}
