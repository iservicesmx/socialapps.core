$(document).ready(function() {
	$('#content').corner("round 0.333em");	
	$('.block-content H1').corner("cc:#000");		
	$('UL#navigation LI A').corner("cc:#8bc8ec");
	$('#nav-menu, .title, .content-title').corner("top");
	$('#nav-menu .current A').corner("round 3px");	
/*	$('.button').corner("round 0.5em");	*/
	$('tr:nth-child(even)').addClass('evenDts');
	$('tr.odd').addClass('oddDtr');	
	$('tr:nth-child(odd)').addClass('oddNtr');
});
