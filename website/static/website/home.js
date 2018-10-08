!function r(o,s,c){function d(a,t){if(!s[a]){if(!o[a]){var n="function"==typeof require&&require;if(!t&&n)return n(a,!0);if(p)return p(a,!0);var e=new Error("Cannot find module '"+a+"'");throw e.code="MODULE_NOT_FOUND",e}var i=s[a]={exports:{}};o[a][0].call(i.exports,function(t){var n=o[a][1][t];return d(n||t)},i,i.exports,r,o,s,c)}return s[a].exports}for(var p="function"==typeof require&&require,t=0;t<c.length;t++)d(c[t]);return d}({1:[function(t,n,a){"use strict";a.__esModule=!0;var e=function(){function t(t){this.selection=t,this.scale=d3.scaleUtc()}return t.prototype.set_range=function(t){this.scale.range(t)},t.prototype.set_domain=function(t){this.scale.domain(t)},t.prototype.set_position=function(t){this.position=t},t.prototype.draw=function(){var t=new Date,n=new Date(Date.UTC(t.getFullYear(),t.getMonth(),t.getDate())),a=this.position[0],e=this.position[1],i=this.scale;this.selection.attr("transform","translate("+a+", "+e+")"),this.selection.transition().call(d3.axisBottom(i)),this.selection.selectAll("g.tick text").filter(function(t){return t.getTime()==n.getTime()}).attr("fill","blue")},t}();a.XAxis=e;var i=function(){function t(t){this.selection=t,this.scale=d3.scaleLinear()}return t.prototype.set_range=function(t){this.scale.range(t)},t.prototype.set_domain=function(t){this.scale.domain(t)},t.prototype.set_position=function(t){this.position=t},t.prototype.draw=function(){var t=this.position[0],n=this.position[1],a=this.scale;this.selection.attr("transform","translate("+t+", "+n+")"),this.selection.transition().call(d3.axisLeft(a).tickFormat(function(t){return"£"+t.toLocaleString(void 0,{maximumFractionDigits:0,minimumFractionDigits:0})}))},t}();a.YAxis=i},{}],2:[function(t,n,a){"use strict";a.__esModule=!0;var e=t("./canvas"),i=t("./tooltip"),r=t("./axis"),u=new i.ToolTip,o=function(){function t(t,n,a){void 0===a&&(a={top:10,left:60,right:20,bottom:40}),this.selection=t,this.balances=n,this.padding=a,this.canvas=new e.Canvas(this.selection.select("#canvas")),this.plot_area=this.canvas.selection.select("#plot-area"),this.x_axis=new r.XAxis(this.canvas.selection.select("#x-axis")),this.y_axis=new r.YAxis(this.canvas.selection.select("#y-axis")),this.set_x_axis_position(),this.set_x_axis_range(),this.set_x_axis_domain(),this.set_y_axis_position(),this.set_y_axis_range(),this.set_y_axis_domain()}return t.prototype.resize=function(){this.canvas.width=this.canvas.get_width(),this.canvas.height=this.canvas.get_height(),this.set_x_axis_range(),this.set_x_axis_domain(),this.set_y_axis_range(),this.set_y_axis_domain(),this.draw()},t.prototype.set_x_axis_position=function(t){var n=this.padding,a=this.canvas.height;void 0===t&&(t=[n.left,a-n.bottom]),this.x_axis.set_position(t)},t.prototype.set_x_axis_range=function(t){void 0===t&&(t=[0,this.canvas.width-this.padding.left-this.padding.right]),this.x_axis.set_range(t)},t.prototype.set_x_axis_domain=function(t){void 0===t&&(t=this.get_x_domain()),this.x_axis.set_domain(t)},t.prototype.set_y_axis_position=function(t){var n=this.padding;void 0===t&&(t=[n.left,n.top]),this.y_axis.set_position(t)},t.prototype.set_y_axis_range=function(t){void 0===t&&(t=[this.canvas.height-this.padding.top-this.padding.bottom,0]),this.y_axis.set_range(t)},t.prototype.set_y_axis_domain=function(t){void 0===t&&(t=this.get_y_domain()),this.y_axis.set_domain(t)},t.prototype.draw=function(){this.draw_x_axis(),this.draw_y_axis(),this.draw_bars()},t.prototype.get_x_domain=function(){var t=new Date(Date.parse(d3.min(this.balances,function(t){return t.date}))),n=new Date(Date.parse(d3.max(this.balances,function(t){return t.date})));return t.setDate(t.getDate()-.5),n.setDate(n.getDate()+.5),[t,n]},t.prototype.get_y_domain=function(){var t=d3.min(this.balances,function(t){return t.balance}),n=d3.max(this.balances,function(t){return t.balance});return[0<t?.9*t:1.1*t,0<n?1.1*n:.9*n]},t.prototype.draw_x_axis=function(){this.x_axis.draw()},t.prototype.draw_y_axis=function(){this.y_axis.draw()},t.prototype.draw_bars=function(){var n=null,a=this.x_axis.scale,e=this.y_axis.scale,i=this.padding,t=this.balances,r=this.canvas.width,o=this.plot_area,s=new Date,c=new Date(Date.UTC(s.getFullYear(),s.getMonth(),s.getDate()));function d(t){var n=new Date(t.date);return n.setDate(n.getDate()-.45),i.left+a(n)}function p(t){return 0<=t.balance?i.top+e(t.balance):i.top+n}function l(t){return Math.abs(e(t.balance)-n)}n=e.domain()[0]<0&&0<=e.domain()[1]?e(0):e.domain()[0]<0?e.range()[1]:e.range()[0],o.selectAll(".bar").data(t,function(t){return t.date}).transition().attr("x",d).attr("width",.9*(r-i.left-i.right)/t.length).attr("y",p).attr("height",l),o.selectAll(".bar").data(t,function(t){return t.date}).enter().append("rect").attr("class",function(t){return t.date==c.toISOString().slice(0,10)?"bar bar-today":"bar"}).attr("x",d).attr("y",i.top+n).attr("width",.9*(r-i.left-i.right)/t.length).attr("date",function(t){return t.date}).attr("balance",function(t){return t.balance}).on("mouseover",u.mouseover_callback).on("mouseout",u.mouseout_callback).transition().attr("y",p).attr("height",l),o.selectAll(".bar").data(t,function(t){return t.date}).exit().transition().attr("x",d).attr("width",.9*(r-i.left-i.right)/t.length).attr("y",n).attr("height",0).remove()},t}();a.BalanceChart=o},{"./axis":1,"./canvas":3,"./tooltip":5}],3:[function(t,n,a){"use strict";a.__esModule=!0;var e=function(){function t(t){this.selection=t,this.height=this.get_height(),this.width=this.get_width()}return t.prototype.get_width=function(){return parseInt(this.selection.style("width"))},t.prototype.get_height=function(){return parseInt(this.selection.style("height"))},t}();a.Canvas=e},{}],4:[function(t,n,a){"use strict";a.__esModule=!0,console.log("home.js"),console.log("test9");var e=t("./balance_chart"),i=t("./transactions_table"),l=null,u=null;function f(t){return t.toISOString().slice(0,10)}function r(t,n){var p=n.serializeArray();t.preventDefault(),console.log("move_date_range_callback"),$.get("/get-balances",p,function(t){console.log("success");var n=p[0].value,a=p[1].value;balances=t.data.balances,l.balances=balances,l.resize();var e=$("#date-selector");e.find("#start-input").val(n),e.find("#end-input").val(a);var i=$("#week-forward-form"),r=new Date(n),o=new Date(a);r.setDate(r.getDate()+7),o.setDate(o.getDate()+7);var s=i.find('input[name="start"]'),c=i.find('input[name="end"]');s.val(f(r)),c.val(f(o));var d=$("#week-backward-form");r=new Date(n),o=new Date(a),r.setDate(r.getDate()-7),o.setDate(o.getDate()-7),s=d.find('input[name="start"]'),c=d.find('input[name="end"]'),s.val(f(r)),c.val(f(o)),transactions=t.data.transactions,u.transactions=transactions,u.update()})}$(document).ready(function(){(l=new e.BalanceChart(d3.select("#balance-chart"),balances)).draw(),u=new i.TransactionsTable(d3.select("#transaction-list"),transactions),$("#week-forward-form").on("submit",function(t){r(t,$(this))}),$("#week-backward-form").on("submit",function(t){r(t,$(this))}),$("#center-on-today-form").on("submit",function(t){r(t,$(this))}),$(window).resize(function(){l.resize()}),$("#repeat-checkbox").change(function(t){$(this).prop("checked")?$("#repeat-options-modal").modal("show"):$(this).val("does_not_repeat")}),$("#repeat-options-close-button").click(function(t){$("#repeat-checkbox").prop("checked",!1)}),$('input:radio[name="ends_how"]').change(function(t){"ends-after-n-transactions"==$(this).attr("id")?($("#n-transactions-input").prop("disabled",!1),$("#ends-on-date-input").prop("disabled",!0)):"ends-on-date"==$(this).attr("id")?($("#n-transactions-input").prop("disabled",!0),$("#ends-on-date-input").prop("disabled",!1)):($("#n-transactions-input").prop("disabled",!0),$("#ends-on-date-input").prop("disabled",!0))}),$('input:radio[name="ends_how"]').change(function(t){console.log("change"),"ends-after-n-transactions"==$(this).attr("id")?(console.log("n_transactions"),$("#n-transactions-div").slideDown(),$("#ends-on-date-div").slideUp()):"ends-on-date"==$(this).attr("id")?(console.log("ends on date"),$("#n-transactions-div").slideUp(),$("#ends-on-date-div").slideDown()):(console.log("never"),$("#n-transactions-div").slideUp(),$("#ends-on-date-div").slideUp())}),$("form.repeat-transaction-update-form").submit(function(t){var n=$(this),a=$("#date-selector input[name='start']").val();n.append('<input name="start" value="'+a+'" hidden>');var e=$("#date-selector input[name='end']").val();n.append('<input name="end" value="'+e+'" hidden>')}),$("form#transaction-form").submit(function(t){var n=$(this),a=$("#date-selector input[name='start']").val();n.append('<input name="start" value="'+a+'" hidden>');var e=$("#date-selector input[name='end']").val();n.append('<input name="end" value="'+e+'" hidden>')})})},{"./balance_chart":2,"./transactions_table":6}],5:[function(t,n,a){"use strict";a.__esModule=!0,a.ToolTip=function(){var e=this;this.tooltip=d3.select("#tooltip"),this.mouseover_callback=function(t){e.tooltip.transition().duration(200).style("opacity",.9),e.tooltip.style("opacity",1),e.tooltip.html("<b>"+t.date+"</b><br>£"+t.balance.toFixed(2)).style("left",function(t){var n=parseFloat(e.tooltip.style("width")),a=parseFloat(d3.event.pageX);return parseFloat(d3.select("#canvas").style("width"))<a+n&&(a-=1.1*n),a+"px"}).style("top",d3.event.pageY-28+"px"),d3.select(this).style("opacity",.6)},this.mouseout_callback=function(t){e.tooltip.transition().duration(500).style("opacity",0),d3.select(this).style("opacity",1)}}},{}],6:[function(t,n,a){"use strict";function l(t,n){t.find("input").attr("form",n.attr("id")),t.find('button[type="submit"]').attr("form",n.attr("id")),t.modal("show")}function o(t){var n=$(this),a='input[form="'+n.attr("id")+'"][name="repeat_transaction_id"]',e=$(a).val(),i=$(document.activeElement),r=(a='input[form="'+n.attr("id")+'"][name="date"]',$(a).val()),o=(a='input[form="'+n.attr("id")+'"][name="transaction_date_original"]',$(a).val()),s=(a='input[form="'+n.attr("id")+'"][name="size"]',$(a).val(),a='input[form="'+n.attr("id")+'"][name="transaction_size_original"]',$(a).val(),a='input[form="'+n.attr("id")+'"][name="description"]',$(a).val(),a='input[form="'+n.attr("id")+'"][name="transaction_description_original"]',$(a).val(),r!=o);if(-1!=i.attr("class").indexOf("delete-transaction-button")&&""!=e)d3.event.preventDefault(),0===(c=$("#repeat-transaction-deletion-prompt")).length?$.get("/html-snippets/repeat-transaction-deletion-prompt",function(t){$("body").append(t),l(c=$("#repeat-transaction-deletion-prompt"),n)}):l(c,n);else if(-1!=i.attr("class").indexOf("save-transaction-button")&&""!=e&&1!=s){var c;d3.event.preventDefault(),0===(c=$("#repeat-transaction-update-prompt")).length?$.get("/html-snippets/repeat-transaction-update-prompt",function(t){$("body").append(t),l(c=$("#repeat-transaction-update-prompt"),n)}):l(c,n)}else{var d=$("#date-selector #start-input").attr("value"),p=$("#date-selector #end-input").attr("value");n.append('<input name="start" value="'+d+'">'),n.append('<input name="end" value="'+p+'">')}}a.__esModule=!0;var e=function(){function t(t,n){this.selection=t,this.transactions=n,this.update()}return t.prototype.update=function(){var t=this.selection.selectAll(".transaction").data(this.transactions,function(t){return t.date+"_"+t.index}),n=t.enter().append("tr").attr("class","transaction"),a=n.append("form").attr("id",function(t){return"transaction-modify-form-"+t.id}).attr("action","/modify-transaction").attr("method","post").attr("hidden",!0);a.append("input").attr("hidden",!0).attr("name","csrfmiddlewaretoken").attr("value",csrf_token),a.on("submit",o),(e=n.append("td")).append("input").attr("class","transaction-date date-input form-control").attr("type","date").attr("name","date").attr("value",function(t){return t.date}).attr("form",function(t){return"transaction-modify-form-"+t.id}),e.append("input").attr("hidden",!0).attr("name","transaction_date_original").attr("value",function(t){return t.date}).attr("form",function(t){return"transaction-modify-form-"+t.id});var e,i=(e=n.append("td")).append("div").attr("class","input-group"),r=i.append("div").attr("class","input-group-prepend").append("span");r.attr("class","input-group-text").style("background-color","#F8F8F8"),r.html("£"),i.append("input").attr("class","transaction-size transaction-size-input form-control").attr("type","number").attr("step","0.01").attr("name","size").style("float","right").attr("value",function(t){return t.size.toFixed(2)}).attr("form",function(t){return"transaction-modify-form-"+t.id}),e.append("input").attr("hidden",!0).attr("name","transaction_size_original").attr("value",function(t){return t.size}).attr("form",function(t){return"transaction-modify-form-"+t.id}),(e=n.append("td")).append("input").attr("class","transaction-description description-input form-control").attr("name","description").attr("form",function(t){return"transaction-modify-form-"+t.id}).attr("value",function(t){return t.description}),e.append("input").attr("hidden",!0).attr("name","transaction_description_original").attr("value",function(t){return t.description}).attr("form",function(t){return"transaction-modify-form-"+t.id}),n.append("td").append("span").attr("class","transaction-balance balance-input form-control").attr("name","balance").attr("form",function(t){return"transaction-modify-form-"+t.id}).html(function(t){return"£"+t.closing_balance.toLocaleString(void 0,{maximumFractionDigits:2,minimumFractionDigits:2})}),n.append("td").append("input").attr("class","save-transaction-button btn btn-primary").attr("type","submit").attr("name","action").attr("form",function(t){return"transaction-modify-form-"+t.id}).attr("value","update"),n.append("td").append("button").attr("class","delete-transaction-button btn btn-primary").attr("form",function(t){return"transaction-modify-form-"+t.id}).attr("type","submit").attr("name","action").attr("value","delete").html("Delete"),n.append("input").attr("class","id").attr("name","id").attr("type","hidden").attr("form",function(t){return"transaction-modify-form-"+t.id}).attr("value",function(t){return t.id}),n.append("input").attr("class","repeat-transaction-id").attr("name","repeat_transaction_id").attr("type","hidden").attr("form",function(t){return"transaction-modify-form-"+t.id}).attr("value",function(t){return t.repeat_transaction_id}),t.exit().remove()},t}();a.TransactionsTable=e},{}]},{},[4]);
//# sourceMappingURL=home.js.map
