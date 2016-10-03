CHART = document.getElementById('mileage_canvas');
lineChart = new Chart(CHART, {
  type: 'line',
  data: g,
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      yAxes: [{
        ticks: {
          userCallback: function(v) { return epoch_to_hh_mm_ss(v) },
          stepSize: 30
        }
      }],
      xAxes: [{
          ticks: {
            autoSkip: false
          }
      }]
    },
    tooltips: {
      callbacks: {
        label: function(tooltipItem, data) {
          return data.datasets[tooltipItem.datasetIndex].label + ': ' + epoch_to_hh_mm_ss(tooltipItem.yLabel)
        }
      }
    }
  }
});

function epoch_to_hh_mm_ss(epoch) {
  return new Date(epoch*1000).toISOString().substr(12, 7)
}
