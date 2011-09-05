/*

jQuery(function($){
	$('dt:nth-child(even)').addClass('evenDts');

});
*/

	$(document).ready(function() {
		$('tr:nth-child(even)').addClass('evenDts');
		$('tr.odd').addClass('oddDtr');	
		$('tr:nth-child(odd)').addClass('oddNtr');		
		
	});
