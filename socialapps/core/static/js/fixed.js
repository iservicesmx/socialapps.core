	$(document).ready(function() {
		$('#content').corner("round 0.333em");	
		$('.block-content H1').corner("cc:#000");		
		$('UL#navigation LI A').corner("cc:#8bc8ec");
		$('#nav-menu, .title').corner("top");
/*		$('#nav-menu, .title').css('box-shadow','0 1px 3px #222;');*/
		$('#nav-menu .current a, ul#nav-menu li a:hover').corner("round 3px");		
		$('tr:nth-child(even)').addClass('evenDts');
		$('tr.odd').addClass('oddDtr');	
		$('tr:nth-child(odd)').addClass('oddNtr');		
		$('.button').corner("round 0.5em");			
	});
