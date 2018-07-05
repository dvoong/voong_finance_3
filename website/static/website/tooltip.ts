declare var d3;

function ToolTip(){
    var that = this;

    this.tooltip = d3.select('#tooltip');

    this.mouseover_callback = function(d){
	that.tooltip.transition()
            .duration(200)
            .style("opacity", .9);
	that.tooltip.style("opacity", 1);
	that.tooltip.html("<b>" + d.date + "</b>" + "<br>£" + d.balance.toFixed(2))
            .style("left", function(e){
		var tooltip_width = parseFloat(that.tooltip.style('width'));
		var left = parseFloat(d3.event.pageX);
		var canvas_width = parseFloat(d3.select('#canvas').style('width'));
		if(left + tooltip_width > canvas_width){
		    left = left - tooltip_width * 1.1
		}
		return left + "px"
	    })
	    .style("top", (d3.event.pageY - 28) + "px");
	d3.select(this)
	    .style('opacity', 0.6);
    };

    this.mouseout_callback = function(d){
	that.tooltip.transition()
            .duration(500)
            .style("opacity", 0);
	d3.select(this)
	    .style('opacity', 1)
    };
    
}

export { ToolTip };
