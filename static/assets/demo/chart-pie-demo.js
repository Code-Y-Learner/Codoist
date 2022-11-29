

// Pie Chart Example
var labels = ["Work","Break"];
var label = [];
var backgroundColors = ['#4e73df', '#1cc88a'];
var backgroudColor = [];
var hoverbackgroundColors = ['#2e59d9', '#17a673'];
var hoverbackgroudColor = [];
for (var i = 0; i < Object.values(timer_data).length; i++) {
  label.push(labels[i % labels.length]);
}
for (var i = 0; i < Object.values(timer_data).length; i++) {
  backgroudColor.push(backgroundColors[i % backgroundColors.length]);
}
for (var i = 0; i < Object.values(timer_data).length; i++) {
  hoverbackgroudColor.push(hoverbackgroundColors[i % hoverbackgroundColors.length]);
}
var ctx = document.getElementById("myPieChart");
var myPieChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: label,
    datasets: [{
      data: Object.values(timer_data),
      backgroundColor: backgroudColor,
      hoverBackgroundColor: hoverbackgroudColor,
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    legend: {
      display: false
    }
  }
});

// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';