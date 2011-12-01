/**
 @preserve CLEditor Image Upload Plugin v1.0.0
 http://premiumsoftware.net/cleditor
 requires CLEditor v1.3.0 or later
 
 Copyright 2011, Dmitry Dedukhin
 Plugin let you either to upload image or to specify image url.
*/

(function($) {
	// Define the image button by replacing the standard one
	$.cleditor.buttons.image = {
		name: 'image',
		title: 'Insert/Upload Image',
		command: 'insertimage',
		popupName: 'image',
		popupClass: 'cleditorPrompt',
		stripIndex: $.cleditor.buttons.image.stripIndex,
		buttonClick: imageButtonClick,
		uploadUrl: '/uploadImage' // default url
	};
	
	$.cleditor.buttons.link = {
		name: 'link',
		title: 'Insert Hyperlink,',
		command: 'createlink',
		popupName: 'ext-url',
		popupClass: 'cleditorPrompt',
		stripIndex: $.cleditor.buttons.link.stripIndex,		
		buttonClick: urlButtonClick,
	};

	function closePopup(editor) {
		editor.hidePopups();
		editor.focus();
	}

	function imageButtonClick(e, data) {
		var editor = data.editor,
			$text = $(data.popup).find(':text.url'),
			url = $.trim($text.val()),
            $existing = $(data.popup).find('iframe[name="existing"]').contents().find('.selected-size');
			$iframe = $(data.popup).find('iframe[name="__upload_iframe"]'),
			$file = $(data.popup).find(':file');

		// clear previously selected file and url
		$file.val('');
        $(data.popup).find('iframe[name="existing"]').contents().find('.selected-object').hide();
		$existing.attr('value', '');
		
        var $tabs = $('.browser-tabs').tabs();
        $tabs.tabs('select', 0);
        var selected = '#existing';

        $('.browser-tabs').bind('tabsselect', function(event, ui) {
            selected = $(ui.tab).attr('href');
        })
		
		$(data.popup)
			.children(":button")
			.unbind("click")
			.bind("click", function(e) {
                $existing = $(data.popup).find('iframe[name="existing"]').contents().find('.selected-size').val();
                if (selected == '#existing' && $existing != undefined) {
                    editor.execCommand(data.command, $existing, null, data.button);
                    closePopup(editor);
				} else if(selected == '#upload' && $file.val()) { // proceed if any file was selected
                    $iframe.bind('load', function() {
            			var file_url;
    				    try {
    					    file_url = $iframe.get(0).contentWindow.document.body.innerHTML;
    				    } catch(e) {};
    				    if(file_url) {
    					    editor.execCommand(data.command, file_url, null, data.button);
    				    } else {
    					    alert('An error occured during upload!');
    				    }
    				    $iframe.unbind('load');
    				    closePopup(editor);
    			    });
        		    $(data.popup).find('form').attr('action', $.cleditor.buttons.image.uploadUrl).submit();
        		} else if (selected == '#url' && $text.val() != '') {
					editor.execCommand(data.command, $text.val(), null, data.button);
					closePopup(editor);
				}
			});
	}
	
	function urlButtonClick(e, data) {
		var editor = data.editor,
			$text = $(data.popup).find(':text.url'),
			url = $.trim($text.val()),
            $existing = $(data.popup).find('iframe[name="existing"]').contents().find('.url');

        if (editor.selectedText() === "") {
            editor.showMessage('A selection is required when inserting a link', data.button);
            return false;
        }
            
		// clear previously selected file and url
		$text.val('').focus();
        $(data.popup).find('iframe[name="existing"]').contents().find('.selected-url').hide();
		$existing.attr('value', '');
		
        var $tabs = $('.browser-tabs').tabs();
        $tabs.tabs('select', 0);
        var selected = '#link-url';
        
        $('.browser-tabs').bind('tabsselect', function(event, ui) {
            selected = $(ui.tab).attr('href');
        })

        $(data.popup).find('.save-link').unbind('click').bind('click', function(e) {
            $existing = $(data.popup).find('iframe[name="existing"]').contents().find('.url').val();
            if (selected == '#existing-url' && $existing != undefined) {
                editor.execCommand(data.command, $existing, $existing, data.button);
                closePopup(editor);
            } else if (selected == '#link-url' && $text.val() != '') {
                editor.execCommand(data.command, $text.val(), $text.val(), data.button);
                closePopup(editor);
            }            
            return false;
        });
	}
})(jQuery);
