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

// =========
// Canvas
// =========

class Canvas {
    width: number;
    height: number;

    constructor(public selection){
	this.height = this.get_height();
	this.width = this.get_width();
    }

    get_width(): number {
	return parseInt(this.selection.style('width'));	
    }

    get_height(): number {
	return parseInt(this.selection.style('height'));
    }
    
}

// =========
// X-Axis
// =========

class XAxis {
    scale;
    position: [number, number];

    constructor(public selection){
	this.scale = d3.scaleUtc();
    };

    set_range(range: [number, number]): void {
	this.scale.range(range)
    }

    set_domain(domain: [Date, Date]): void {
	this.scale.domain(domain);
    }

    set_position(position: [number, number]): void {
	this.position = position;
    }

    draw(): void {
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
}

// =========
// Y-Axis
// =========

class YAxis{
    scale;
    position: [number, number];
    
    constructor(public selection){
	this.scale = d3.scaleLinear();
    }

    set_range(range: [number, number]): void {
	this.scale.range(range);
    }

    set_domain(domain: [number, number]): void {
	this.scale.domain(domain);
    }

    set_position(position: [number, number]): void {
	this.position = position;
    }

    draw(): void {
	var x = this.position[0];
	var y = this.position[1];
	var scale = this.scale;
	function tick_formatter(t){
	    return '£' + t.toLocaleString()
	}
	
	this.selection.attr('transform', 'translate(' + x + ', ' + y + ')');
	this.selection.transition().call(d3.axisLeft(scale).tickFormat(tick_formatter));
    }
}

// ==============
// Balance Chart
// ==============

class BalanceChart {
    canvas: Canvas;
    plot_area;
    x_axis: XAxis;
    y_axis: YAxis;
    constructor(public selection,
		public balances: Object[],
		public padding = {top: 10, left: 60, right: 20, bottom: 40}){
	this.canvas = new Canvas(this.selection.select('#canvas'));
	this.plot_area = this.canvas.selection.select('#plot-area');
	this.x_axis = new XAxis(this.canvas.selection.select('#x-axis'));
	this.y_axis = new YAxis(this.canvas.selection.select('#y-axis'));
	this.set_x_axis_position();
	this.set_x_axis_range();
	this.set_x_axis_domain();
	this.set_y_axis_position();
	this.set_y_axis_range();
	this.set_y_axis_domain();
    }

    resize(){
	this.canvas.width = this.canvas.get_width();
	this.canvas.height = this.canvas.get_height();
	this.set_x_axis_range();
	this.set_x_axis_domain();
	this.set_y_axis_range();
	this.set_y_axis_domain();
	this.draw();
    }


    set_x_axis_position(position?: [number, number]){
	var padding = this.padding;
	var canvas_height = this.canvas.height;
	if (position === void 0) { position = [padding.left, canvas_height - padding.bottom]; }
	this.x_axis.set_position(position);
    }
    
    set_x_axis_range(range?: [number, number]): void {
	if (range === void 0) { range = [0, this.canvas.width - this.padding.left - this.padding.right]; }
	this.x_axis.set_range(range);
    }

    set_x_axis_domain(domain?: [Date, Date]): void {
	if (domain === void 0) { domain = this.get_x_domain(); }
	this.x_axis.set_domain(domain);
    }

    set_y_axis_position(position?: [number, number]): void {
	var padding = this.padding;
	if (position === void 0) { position =  [padding.left, padding.top]; }
	this.y_axis.set_position(position);
    }

    set_y_axis_range(range?: [number, number]): void {
	if (range === void 0) { range = [this.canvas.height - this.padding.top - this.padding.bottom, 0]; }
	this.y_axis.set_range(range);
    }

    set_y_axis_domain(domain?: [number, number]): void {
	if (domain === void 0) { domain = this.get_y_domain(); }
	this.y_axis.set_domain(domain);
    }

    draw(): void {
	this.draw_x_axis();
	this.draw_y_axis();
	this.draw_bars();
    }

    get_x_domain() : [Date, Date] {
	var start: Date = new Date(Date.parse(d3.min(this.balances, function(d){return d.date})));
	var end = new Date(Date.parse(d3.max(this.balances, function(d){return d.date})));

	start.setDate(start.getDate() - 0.5);
	end.setDate(end.getDate() +0.5);
	return [start, end];

    }

    get_y_domain(): [number, number] {
	var balance_min = d3.min(this.balances, function(d){return d.balance});
	var balance_max = d3.max(this.balances, function(d){return d.balance});
	var y_min = balance_min > 0 ? 0.9 * balance_min : 1.1 * balance_min;
	var y_max = balance_max > 0 ? 1.1 * balance_max : 0.9 * balance_max;
	return [y_min, y_max];
	
    }

    draw_x_axis(): void {
	this.x_axis.draw();
    }

    draw_y_axis(): void {
	this.y_axis.draw();
    }

    draw_bars(): void {
	
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
	    var x_lower = new Date(d.date);
	    x_lower.setDate(x_lower.getDate() - 0.45);
	    return padding.left + x_scale(x_lower);
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

var balance_chart = null;
var tooltips = null;

declare var balances: any[];
declare var $: any;
declare var d3: any;

//declare var staticData: any;
//declare var balances: any;

