"use strict";
exports.__esModule = true;
function ToolTip() {
    var that = this;
    this.tooltip = d3.select('#tooltip');
    this.mouseover_callback = function (d) {
        that.tooltip.transition()
            .duration(200)
            .style("opacity", .9);
        that.tooltip.style("opacity", 1);
        that.tooltip.html("<b>" + d.date + "</b>" + "<br>£" + d.balance.toFixed(2))
            .style("left", (d3.event.pageX) + "px")
            .style("top", (d3.event.pageY - 28) + "px");
        d3.select(this)
            .style('opacity', 0.6);
    };
    this.mouseout_callback = function (d) {
        that.tooltip.transition()
            .duration(500)
            .style("opacity", 0);
        d3.select(this)
            .style('opacity', 1);
    };
}
exports.ToolTip = ToolTip;
