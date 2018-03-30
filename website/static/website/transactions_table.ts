var d3 = require("d3");

class TransactionsTable {

    constructor(public selection, public transactions: Object[]){
	this.update();
    }

    update(){

	var transactions = this.selection.selectAll('.transaction')
	    .data(this.transactions, function(d){
		return d.date + '_' + d.index;
	    });

	var enter = transactions.enter()
	    .append('tr')
	    .attr('class', 'transaction');

	var form = enter.append('form')
	    .attr('id', function(d){
		return 'transaction-modify-form-' + d.id
	    })
	    .attr('action', '/modify-transaction')
	    .attr('method', 'post')
	    .attr('hidden', true);

	form.append('input')
	    .attr('hidden', true)
	    .attr('name', 'csrfmiddlewaretoken')
	    .attr('value', csrf_token);

	enter.append('td')
	    .attr('class', 'transaction-date')
	    .append('input')
	    .attr('class', 'date-input form-control')
	    .attr('type', 'date')
	    .attr('name', 'date')
	    .attr('value', function(d){return d.date})
	    .attr('form', function(d){return 'transaction-modify-form-' + d.id});

	enter.append('td')
	    .attr('class', 'transaction-size')
	    .append('input')
	    .attr('class', 'transaction-size-input form-control')
	    .attr('type', 'number')
	    .attr('step', '0.01')
	    .attr('name', 'size')
	    .attr('value', function(d){return d.size})
	    .attr('form', function(d){return 'transaction-modify-form-' + d.id});

	enter.append('td')
	    .attr('class', 'transaction-description')
	    .append('input')
	    .attr('class', 'description-input form-control')
	    .attr('name', 'description')
	    .attr('form', function(d){return 'transaction-modify-form-' + d.id})
	    .attr('value', function(d){return d.description});

	enter.append('td')
	    .attr('class', 'transaction-balance')
	    .append('span')
	    .attr('class', 'balance-input form-control')
	    .attr('name', 'balance')
	    .attr('form', function(d){return 'transaction-modify-form-' + d.id})
	    .html(function(d){
		var format_options = {
		    maximumFractionDigits: 2,
		    minimumFractionDigits: 2,
		}
		return '£' + d.closing_balance.toLocaleString(undefined, format_options)
	    });

	enter.append('td')
	    .append('input')
	    .attr('class', 'save-transaction-button btn btn-primary')
	    .attr('type', 'submit')
	    .attr('name', 'action')
	    .attr('form', function(d){return 'transaction-modify-form-' + d.id})
	    .attr('value', 'update');

	enter.append('td')
	    .append('input')
	    .attr('class', 'delete-transaction-button btn btn-primary')
	    .attr('type', 'submit')
	    .attr('name', 'action')
	    .attr('form', function(d){return 'transaction-modify-form-' + d.id})
	    .attr('value', 'delete');

	enter.append('input')
	    .attr('class', 'id')
	    .attr('name', 'id')
	    .attr('type', 'hidden')
	    .attr('form', function(d){return 'transaction-modify-form-' + d.id})
	    .attr('value', function(d){return d.id})

	var exit = transactions.exit();
	exit.remove();

    }
}

export { TransactionsTable };
