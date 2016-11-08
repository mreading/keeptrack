
// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart']});

// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(drawWeekChart);


function drawWeekChart() {
  // Create the data table.
  // var data = google.visualization.arrayToDataTable([
  //       ['Genre', 'Fantasy & Sci Fi', 'Romance', 'Mystery/Crime', 'General',
  //        'Western', 'Literature'],
  //       ['2010', 10, 24, 20, 32, 18, 5],
  //       ['2020', 16, 22, 23, 30, 16, 9],
  //       ['2030', 28, 19, 29, 30, 12, 13]
  //     ]);
  var data = google.visualization.arrayToDataTable(mileage_data);

  var options = {
    width: 600,
    height: 400,
    legend: { position: 'top', maxLines: 3 },
    bar: { groupWidth: '75%' },
    isStacked: true,
  };
  var view = new google.visualization.DataView(data);
  view.setColumns([0, 1, 2, 3, 4, 5, 6])

  // Set chart options
  var options = {'title':'Athlete Mileage',
                 'height':300,
                //  'width':graphSelector.getActiveDivWidth(),
                 'interpolateNulls': true,
                 'pointShape': 'circle',
                 'pointSize': 5,
                //  'colors': ['#6b7a8f', '#f7c331'],
                 'legend':{position:'right'},
                 'isStacked':true
               };

  // Instantiate and draw our chart, passing in some options.
  var chart = new google.visualization.ColumnChart(document.getElementById('mileage_graph'));
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
