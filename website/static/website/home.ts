console.log('home.js');

import { BalanceChart } from "./balance_chart";

var balance_chart = null;
var tooltips = null;

declare var balances: any[];
declare var $: any;
declare var d3: any;

// ================
// Event triggers
// ================

function toISODateString(date){
    return date.toISOString().slice(0, 10);
}

$(document).ready(function(){
    balance_chart = new BalanceChart(d3.select('#balance-chart'), balances);
    balance_chart.draw();
});

$(document).ready(function(){
    
    $('#week-forward-form').on('submit', function(e){
	var form = $(this);
	
	function success(d){
	    balances = d['data'];
	    balance_chart.balances = balances;
	    balance_chart.resize();
	    $('#date-selector #start-input').val(args[0].value);
	    $('#date-selector #end-input').val(args[1].value);

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
	    $('#date-selector #start-input').val(args[0].value);
	    $('#date-selector #end-input').val(args[1].value);

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
    
    $(window).resize(function(){
	balance_chart.resize();
    });

});
