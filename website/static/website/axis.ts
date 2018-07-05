declare var d3;

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
	var now = new Date();
	var today = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));
	var x = this.position[0];
	var y = this.position[1];
	var scale = this.scale;
	
	this.selection.attr('transform', 'translate(' + x + ', ' + y + ')');
	this.selection.transition().call(d3.axisBottom(scale));
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
	    return '£' + t.toLocaleString(
		undefined,
		{
		    maximumFractionDigits: 2,
		    minimumFractionDigits: 2,
		})
	}
	
	this.selection.attr('transform', 'translate(' + x + ', ' + y + ')');
	this.selection.transition().call(d3.axisLeft(scale).tickFormat(tick_formatter));
    }
}

export { XAxis, YAxis };
