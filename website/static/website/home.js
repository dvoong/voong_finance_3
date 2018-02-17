console.log('home.js');

$(document).ready(function(){
    draw_chart();
});

function draw_chart(){
    var padding = {top: 10, left: 60, right: 20, bottom: 40};
    var balance_chart = d3.select('#balance-chart');
    var canvas = balance_chart.select('#canvas');
    var x_axis = canvas.select('#x-axis');
    var y_axis = canvas.select('#y-axis');
    var plot_area = canvas.select('#plot-area');

    var canvas_height = parseInt(canvas.style('height'));
    var canvas_width = parseInt(canvas.style('width'));

    draw_x_axis(x_axis, canvas_width, canvas_height, padding);
    draw_y_axis(y_axis, canvas_width, canvas_height, padding);
}

function draw_x_axis(x_axis, canvas_width, canvas_height, padding){
    x_axis.attr('transform', 'translate(' + padding.left + ', ' + (canvas_height - padding.bottom) + ')');

    var start = new Date(d3.min(balances, function(d){return d.date}));
    var end = new Date(d3.max(balances, function(d){return d.date}));
    
    var x_min = new Date(start);
    x_min.setDate(start.getDate() - 0.5);
    var x_max = new Date(end);
    x_max.setDate(end.getDate() +0.5);

    var x_scale = d3.scaleUtc()
	.domain([x_min, x_max])
	.range([0, canvas_width - padding.left - padding.right]);

    x_axis.call(d3.axisBottom(x_scale))
}

function draw_y_axis(y_axis, canvas_width, canvas_height, padding){
    y_axis.attr('transform', 'translate(' + padding.left + ', ' + padding.top + ')');

    var y_min = 0;
    var y_max = 1;
    var y_scale = d3.scaleLinear()
	.domain([y_max, y_min])
	.range([0, canvas_height - padding.top - padding.bottom]);

    y_axis.call(d3.axisLeft(y_scale))
}
