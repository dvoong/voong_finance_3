
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

export { Canvas };
