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

    var x_scale = draw_x_axis(x_axis, canvas_width, canvas_height, padding);
    var y_scale = draw_y_axis(y_axis, canvas_width, canvas_height, padding);
    var bars = draw_bars(plot_area, x_scale, y_scale, canvas_width, canvas_height, padding);
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
    return x_scale;
}

function draw_y_axis(y_axis, canvas_width, canvas_height, padding){
    y_axis.attr('transform', 'translate(' + padding.left + ', ' + padding.top + ')');

    var balance_min = d3.min(balances, function(d){return d.balance});
    var balance_max = d3.max(balances, function(d){return d.balance});
    var y_min = balance_min > 0 ? 0.9 * balance_min : 1.1 * balance_min;
    var y_max = balance_max > 0 ? 1.1 * balance_max : 0.9 * balance_max;
    var y_scale = d3.scaleLinear()
	.domain([y_min, y_max])
	.range([canvas_height - padding.top - padding.bottom, 0]);

    y_axis.call(d3.axisLeft(y_scale).tickFormat(function(t){return '£' + t.toLocaleString()}))
    return y_scale;
}

function draw_bars(plot_area, x_scale, y_scale, canvas_width, canvas_height, padding){
    var y_reference = null;
    if(y_scale.domain()[0] < 0 && y_scale.domain()[1] >= 0){
	// 0 is within the y-axis range, set that as the reference
	y_reference = y_scale(0);
    } else if (y_scale.domain()[0] < 0 ) {
	// y-axis range is only negative, set reference to the top of the chart
	y_reference = y_scale.range()[1];
    } else {
	// y-axis range is only positive, set reference to the bottom of the chart
	y_reference = y_scale.range()[0];
    }
    
    plot_area.selectAll('.bar')
	.data(balances)
	.enter()
	.append('rect')
	.attr('class', 'bar')
	.attr('x', function(d){
	    var date = new Date(d.date);
	    var x_lower = new Date(date);
	    x_lower.setDate(x_lower.getDate() - 0.45);
	    x_lower = x_scale(x_lower);
	    return padding.left + x_lower
	})
	.attr('y', padding.top + y_reference)
	.attr('width', 0.9 * (canvas_width - padding.left - padding.right) / balances.length)
	.attr('date', function(d){return d.date})
	.attr('balance', function(d){return d.balance})
	.on('mouseover', tooltips.mouseover_callback)
	.on('mouseout', tooltips.mouseout_callback)
	.transition()
	.attr('y', function(d){
	    if(d.balance >= 0){
	    	return padding.top + y_scale(d.balance);
	    } else {
	    	return padding.top + y_reference;
	    }
	})
	.attr('height', function(d){
	    return Math.abs(y_scale(d.balance) - y_reference)
	})

}

function ToolTip(){
    that = this;

    this.tooltip = d3.select('#tooltip');

    this.mouseover_callback = function(d){
	that.tooltip.transition()
            .duration(200)
            .style("opacity", .9);
	that.tooltip.style("opacity", 1);
	that.tooltip.html(d.date + ": £" + d.balance)
            .style("left", (d3.event.pageX) + "px")
            .style("top", (d3.event.pageY - 28) + "px");
    };

    this.mouseout_callback = function(d){
	that.tooltip.transition()
            .duration(500)
            .style("opacity", 0);
    };
    
}
var tooltips = new ToolTip();
