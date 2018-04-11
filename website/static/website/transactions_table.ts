var d3 = require("d3");
var $ = require("jquery");

function attach_form_and_show_prompt(prompt, form){
    // attach appropriate transaction modification form to the prompt inputs
    prompt.find('input').attr('form', form.attr('id'));
    prompt.find('button[type="submit"]').attr('form', form.attr('id'));
    prompt.modal('show');
}

function submit_delete(d){

    var form = $(this);
    var selector = `input[form="${form.attr("id")}"][name="repeat_transaction_id"]`;
    var repeat_transaction = $(selector).val();
    var btn = $(document.activeElement);

    if(btn.attr('class').indexOf('delete-transaction-button') != -1 && repeat_transaction != ''){

    	d3.event.preventDefault();
    	var prompt = $('#repeat-transaction-deletion-prompt');
    	if(prompt.length === 0){
    	    $.get('/html-snippets/repeat-transaction-deletion-prompt', function(x){
    	    	$('body').append(x);
    	    	prompt = $('#repeat-transaction-deletion-prompt');
    	    	attach_form_and_show_prompt(prompt, form);
    	    });
	} else {
    	    attach_form_and_show_prompt(prompt, form);
    	}
	
    } else if (btn.attr('class').indexOf('save-transaction-button') != -1 &&
	       repeat_transaction != '') {
    	d3.event.preventDefault();
	var prompt = $('#repeat-transaction-update-prompt');
    	if(prompt.length === 0){
    	    $.get('/html-snippets/repeat-transaction-update-prompt', function(x){
    		$('body').append(x);
    		    prompt = $('#repeat-transaction-update-prompt');
    		attach_form_and_show_prompt(prompt, form);
    	    });
    	} else {
    	    attach_form_and_show_prompt(prompt, form);
    	}

    } else {
	var start = $("#date-selector #start-input").attr('value');
	var end = $("#date-selector #end-input").attr('value');
    
	form.append(`<input name="start" value="${start}">`);
	form.append(`<input name="end" value="${end}">`);

    }
}

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

	form.on('submit', submit_delete);

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
	    .append('button')
	    .attr('class', 'delete-transaction-button btn btn-primary')
	    .attr('form', function(d){return 'transaction-modify-form-' + d.id})
	    .attr('type', 'submit')
	    .attr('name', 'action')
	    .attr('value', 'delete')
	    .html('Delete');

	enter.append('input')
	    .attr('class', 'id')
	    .attr('name', 'id')
	    .attr('type', 'hidden')
	    .attr('form', function(d){return 'transaction-modify-form-' + d.id})
	    .attr('value', function(d){return d.id})

	enter.append('input')
	    .attr('class', 'repeat-transaction-id')
	    .attr('name', 'repeat_transaction_id')
	    .attr('type', 'hidden')
	    .attr('form', function(d){return 'transaction-modify-form-' + d.id})
	    .attr('value', function(d){return d.repeat_transaction_id});

	var exit = transactions.exit();
	exit.remove();

    }
}

export { TransactionsTable };
