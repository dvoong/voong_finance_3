console.log('home.js');

// =========
// Tool Tip
// =========

function ToolTip(){
    var that = this;

    this.tooltip = d3.select('#tooltip');

    this.mouseover_callback = function(d){
	that.tooltip.transition()
            .duration(200)
            .style("opacity", .9);
	that.tooltip.style("opacity", 1);
	that.tooltip.html("<b>" + d.date + "</b>" + "<br>£" + d.balance.toFixed(2))
            .style("left", (d3.event.pageX) + "px")
            .style("top", (d3.event.pageY - 28) + "px");
	d3.select(this)
	    .style('opacity', 0.6)
    };

    this.mouseout_callback = function(d){
	that.tooltip.transition()
            .duration(500)
            .style("opacity", 0);
	d3.select(this)
	    .style('opacity', 1)
    };
    
}


// ==============
// Balance Chart
// ==============

function BalanceChart(selection, balances){
    var that = this;
    that.selection = selection;
    that.balances = balances;
    that.padding = {top: 10, left: 60, right: 20, bottom: 40};    
    that.canvas = new Canvas(selection.select('#canvas'));
    that.plot_area = that.canvas.selection.select('#plot-area');
    that.x_axis = new XAxis(that.canvas.selection.select('#x-axis'));
    that.y_axis = new YAxis(that.canvas.selection.select('#y-axis'));
    that.set_x_axis_position();
    that.set_x_axis_range();
    that.set_x_axis_domain();
    that.set_y_axis_position();
    that.set_y_axis_range();
    that.set_y_axis_domain();
}

BalanceChart.prototype.resize = function(){
    this.canvas.width = this.canvas.get_width();
    this.canvas.height = this.canvas.get_height();
    this.set_x_axis_range();
    this.set_x_axis_domain();
    this.set_y_axis_range();
    this.set_y_axis_domain();
    this.draw();
}

BalanceChart.prototype.set_x_axis_position = function(position){
    var padding = this.padding;
    var canvas_height = this.canvas.height;
    position = position ? position !== undefined : [padding.left, canvas_height - padding.bottom];
    this.x_axis.position = position;
}

BalanceChart.prototype.set_y_axis_position = function(position){
    var padding = this.padding;
    position = position ? position !== undefined : [padding.left, padding.top];
    this.y_axis.position = position;
}

BalanceChart.prototype.set_x_axis_range = function(range){
    range = range ? range !== undefined : [0, this.canvas.width - this.padding.left - this.padding.right];
    this.x_axis.set_range(range);
}

BalanceChart.prototype.set_y_axis_range = function(range){
    range = range ? range !== undefined : [this.canvas.height - this.padding.top - this.padding.bottom, 0];
    this.y_axis.set_range(range);
}

BalanceChart.prototype.set_x_axis_domain = function(domain){
    var domain = domain ? domain !== undefined : this.get_x_domain();
    this.x_axis.set_domain(domain);
}

BalanceChart.prototype.set_y_axis_domain = function(domain){
    domain = domain ? domain !== undefined : this.get_y_domain();
    this.y_axis.set_domain(domain);
}

BalanceChart.prototype.get_x_domain = function(){
    var start = new Date(Date.parse(d3.min(this.balances, function(d){return d.date})));
    var end = new Date(Date.parse(d3.max(this.balances, function(d){return d.date})));

    var x_min = new Date(start);
    x_min.setDate(start.getDate() - 0.5);
    var x_max = new Date(end);
    x_max.setDate(end.getDate() +0.5);
    return [x_min, x_max];

}

BalanceChart.prototype.get_y_domain = function(){
    var balance_min = d3.min(this.balances, function(d){return d.balance});
    var balance_max = d3.max(this.balances, function(d){return d.balance});
    var y_min = balance_min > 0 ? 0.9 * balance_min : 1.1 * balance_min;
    var y_max = balance_max > 0 ? 1.1 * balance_max : 0.9 * balance_max;
    return [y_min, y_max];
    
}

BalanceChart.prototype.draw_x_axis = function(){
    this.x_axis.draw();
}

BalanceChart.prototype.draw_y_axis = function(){
    this.y_axis.draw();
}

BalanceChart.prototype.draw_bars = function(){
    
    var that = this;
    var y_reference = null;
    var x_scale = this.x_axis.scale;
    var y_scale = this.y_axis.scale;
    var padding = this.padding;
    var balances = this.balances
    var canvas_width = this.canvas.width;
    var plot_area = this.plot_area;
    
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

    function set_x(d){
	var date = new Date(d.date);
	var x_lower = new Date(date);
	x_lower.setDate(x_lower.getDate() - 0.45);
	x_lower = x_scale(x_lower);
	return padding.left + x_lower
    }
    
    function set_y(d){
	if(d.balance >= 0){
	    return padding.top + y_scale(d.balance);
	} else {
	    return padding.top + y_reference;
	}
    }

    function set_height(d){
	return Math.abs(y_scale(d.balance) - y_reference)
    }

    plot_area.selectAll('.bar')
	.data(balances, function(d){return d.date})
	.transition()
	.attr('x', set_x)
	.attr('width', 0.9 * (canvas_width - padding.left - padding.right) / balances.length)
	.attr('y', set_y)
	.attr('height', set_height);
    
    plot_area.selectAll('.bar')
	.data(balances, function(d){return d.date})
	.enter()
	.append('rect')
	.attr('class', 'bar')
	.attr('x', set_x)
	.attr('y', padding.top + y_reference)
	.attr('width', 0.9 * (canvas_width - padding.left - padding.right) / balances.length)
	.attr('date', function(d){return d.date})
	.attr('balance', function(d){return d.balance})
	.on('mouseover', tooltips.mouseover_callback)
	.on('mouseout', tooltips.mouseout_callback)
	.transition()
	.attr('y', set_y)
	.attr('height', set_height);

    plot_area.selectAll('.bar')
	.data(balances, function(d){return d.date})
	.exit()
	.transition()
	.attr('x', set_x)
	.attr('width', 0.9 * (canvas_width - padding.left - padding.right) / balances.length)
	.attr('y', y_reference)
	.attr('height', 0)
	.remove();
    
}

BalanceChart.prototype.draw = function(){
    this.draw_x_axis();
    this.draw_y_axis();
    this.draw_bars();
}

// =========
// X-Axis
// =========

function XAxis(selection){
    var that = this;
    that.selection = selection;
    that.scale = d3.scaleUtc();
}

XAxis.prototype.set_range = function(range){
    this.scale.range(range);
}

XAxis.prototype.set_domain = function(domain){
    this.scale.domain(domain);
}

XAxis.prototype.draw = function(){
    var x = this.position[0];
    var y = this.position[1];
    var scale = this.scale;
    this.selection.attr('transform', 'translate(' + x + ', ' + y + ')');
    this.selection.transition().call(d3.axisBottom(scale));

    var now = new Date();
    var today = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));
    this.selection
	.selectAll('g.tick text')
	.filter(function(d){
	    return d.getTime() == today.getTime()
	})
	.attr('fill', 'blue');
}


// =========
// Y-Axis
// =========

function YAxis(selection){
    var that = this;
    that.selection = selection;
    that.scale = d3.scaleLinear()
}

YAxis.prototype.set_range = function(range){
    this.scale.range(range);
}

YAxis.prototype.set_domain = function(domain){
    this.scale.domain(domain);
}

YAxis.prototype.draw = function(){
    var x = this.position[0];
    var y = this.position[1];
    var scale = this.scale;
    function tick_formatter(t){
	return '£' + t.toLocaleString()
    }
    
    this.selection.attr('transform', 'translate(' + x + ', ' + y + ')');
    this.selection.transition().call(d3.axisLeft(scale).tickFormat(tick_formatter));
}


// =========
// Canvas
// =========

function Canvas(selection){
    var that = this;
    that.selection = selection;
    that.width = this.get_width();
    that.height = this.get_height();
	
}

Canvas.prototype.get_width = function(width){
    return parseInt(this.selection.style('width'));
}

Canvas.prototype.get_height = function(){
    return parseInt(this.selection.style('height'));
}

// ================
// Event triggers
// ================

function toISODateString(date){
    return date.toISOString().slice(0, 10);
}

$(document).ready(function(){
    
    $('#week-forward-form').on('submit', function(e){
	var form = $(this);
	
	function success(d){
	    balances = d['data'];
	    balance_chart.balances = balances;
	    balance_chart.resize();
	    $('body').attr('date_range_start', args[0].value);
	    $('body').attr('date_range_end', args[1].value);

	    var start_new = new Date(args[0].value);
	    var end_new = new Date(args[1].value);
	    start_new.setDate(start_new.getDate() + 7);
	    end_new.setDate(end_new.getDate() + 7);
	    var start_input = form.find('input[name="start"]');
	    var end_input = form.find('input[name="end"]');
	    start_input.val(toISODateString(start_new));
	    end_input.val(toISODateString(end_new));

	    var form_backward = $('#week-backward-form');
	    var start_new = new Date(args[0].value);
	    var end_new = new Date(args[1].value);
	    start_new.setDate(start_new.getDate() - 7);
	    end_new.setDate(end_new.getDate() - 7);
	    var start_input = form_backward.find('input[name="start"]');
	    var end_input = form_backward.find('input[name="end"]');
	    start_input.val(toISODateString(start_new));
	    end_input.val(toISODateString(end_new));

	}
	
	e.preventDefault();
	var url = '/get-balances';
	var args = form.serializeArray();
	$.get(url, args, success);

    });
    
    $('#week-backward-form').on('submit', function(e){
	var form = $(this);
	
	function success(d){
	    balances = d['data'];
	    balance_chart.balances = balances;
	    balance_chart.resize();
	    $('body').attr('date_range_start', args[0].value);
	    $('body').attr('date_range_end', args[1].value);

	    var start_new = new Date(args[0].value);
	    var end_new = new Date(args[1].value);
	    start_new.setDate(start_new.getDate() - 7);
	    end_new.setDate(end_new.getDate() - 7);
	    var start_input = form.find('input[name="start"]');
	    var end_input = form.find('input[name="end"]');
	    start_input.val(toISODateString(start_new));
	    end_input.val(toISODateString(end_new));

	    var form_forward = $('#week-forward-form');
	    var start_new = new Date(args[0].value);
	    var end_new = new Date(args[1].value);
	    start_new.setDate(start_new.getDate() + 7);
	    end_new.setDate(end_new.getDate() + 7);
	    var start_input = form_forward.find('input[name="start"]');
	    var end_input = form_forward.find('input[name="end"]');
	    start_input.val(toISODateString(start_new));
	    end_input.val(toISODateString(end_new));

	}
	
	e.preventDefault();
	var url = '/get-balances';
	var args = form.serializeArray();
	$.get(url, args, success);

    });

});


// =========
// Other
// =========

function resize_window(){
    balance_chart.resize();
    
}

$(document).ready(function(){
    balance_chart = new BalanceChart(d3.select('#balance-chart'), balances);
    tooltips = new ToolTip();
    balance_chart.draw();
});
