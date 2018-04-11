console.log('home.js');
console.log('test2');

declare var balances: any[];

var $ = require("jquery");
global.jQuery = require("jQuery");
var d3 = require("d3");
require('bootstrap');

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

	conosle.log(transactions);
	console.log(balances);
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

    $('input:radio[name="end_condition"]').change(function(e){
	if($(this).attr('id') == 'ends-after-n-occurrences'){
	    $('#n-occurrences-input').prop('disabled', false);
	    $('#ends-on-date-input').prop('disabled', true);
	} else if ($(this).attr('id') == 'ends-on-date'){
	    $('#n-occurrences-input').prop('disabled', true);
	    $('#ends-on-date-input').prop('disabled', false);
	} else {
	    $('#n-occurrences-input').prop('disabled', true);
	    $('#ends-on-date-input').prop('disabled', true);
	}
    });

});
