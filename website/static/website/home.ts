console.log('home.js');
console.log('test7');

declare var $;
declare var d3;
declare var balances: any[];
declare var global;
declare var transactions: any[];

import { BalanceChart } from "./balance_chart";
import { TransactionsTable } from "./transactions_table";

var balance_chart = null;
var transactions_table = null;

function toISODateString(date){
    return date.toISOString().slice(0, 10);
}

function move_date_range_callback(e, form){
    var url = '/get-balances';
    var args = form.serializeArray();
    e.preventDefault();

    console.log('move_date_range_callback');
    function success(d){
	console.log('success');
	
	var start = args[0].value;
	var end = args[1].value;

	balances = d.data.balances;
	balance_chart.balances = balances;
	balance_chart.resize();

	var date_range_selector = $('#date-selector');
	date_range_selector.find('#start-input').val(start);
	date_range_selector.find('#end-input').val(end);

	var form_forward = $('#week-forward-form');
	var start_new = new Date(start);
	var end_new = new Date(end);
	start_new.setDate(start_new.getDate() + 7);
	end_new.setDate(end_new.getDate() + 7);
	var start_input = form_forward.find('input[name="start"]');
	var end_input = form_forward.find('input[name="end"]');
	start_input.val(toISODateString(start_new));
	end_input.val(toISODateString(end_new));

	var form_backward = $('#week-backward-form');
	var start_new = new Date(start);
	var end_new = new Date(end);
	start_new.setDate(start_new.getDate() - 7);
	end_new.setDate(end_new.getDate() - 7);
	var start_input = form_backward.find('input[name="start"]');
	var end_input = form_backward.find('input[name="end"]');
	start_input.val(toISODateString(start_new));
	end_input.val(toISODateString(end_new));

	transactions = d.data.transactions;
	transactions_table.transactions = transactions;
	transactions_table.update();

    }
    
    $.get(url, args, success);
    
}

$(document).ready(function(){

    balance_chart = new BalanceChart(d3.select('#balance-chart'), balances);
    balance_chart.draw();

    transactions_table = new TransactionsTable(d3.select('#transaction-list'), transactions);

    $('#week-forward-form').on('submit', function(e){
    	move_date_range_callback(e, $(this));
    });
    
    $('#week-backward-form').on('submit', function(e){
    	move_date_range_callback(e, $(this));
    });
    
    $('#center-on-today-form').on('submit', function(e){
    	move_date_range_callback(e, $(this));
    });
    
    $(window).resize(function(){
    	balance_chart.resize();
    });

    $('#repeat-checkbox').change(function(e){
	if($(this).prop('checked')){
	    var modal = $('#repeat-options-modal');
	    modal.modal('show');
	} else {
	    $(this).val('does_not_repeat');
	}
    });

    $('#repeat-options-close-button').click(function(e){
	$('#repeat-checkbox').prop('checked', false);
    });

    $('input:radio[name="ends_how"]').change(function(e){
	if($(this).attr('id') == 'ends-after-n-transactions'){
	    $('#n-transactions-input').prop('disabled', false);
	    $('#ends-on-date-input').prop('disabled', true);
	} else if ($(this).attr('id') == 'ends-on-date'){
	    $('#n-transactions-input').prop('disabled', true);
	    $('#ends-on-date-input').prop('disabled', false);
	} else {
	    $('#n-transactions-input').prop('disabled', true);
	    $('#ends-on-date-input').prop('disabled', true);
	}
    });

    $('form.repeat-transaction-update-form').submit(function(e){
	var form = $(this);
	var start = $("#date-selector input[name='start']").val();
	form.append(`<input name="start" value="${start}" hidden>`);
	var end = $("#date-selector input[name='end']").val();
	form.append(`<input name="end" value="${end}" hidden>`);

    });

    $('form#transaction-form').submit(function(e){
	var form = $(this);
	var start = $("#date-selector input[name='start']").val();
	form.append(`<input name="start" value="${start}" hidden>`);
	var end = $("#date-selector input[name='end']").val();
	form.append(`<input name="end" value="${end}" hidden>`);
    });

});
