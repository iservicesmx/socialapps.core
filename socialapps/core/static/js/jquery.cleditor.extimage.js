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
            $existing = $(data.popup).find('iframe[name="existing"]').contents().find('.selected-size'),
			$iframe = $(data.popup).find('iframe[name="__upload_iframe"]'),
			$file = $(data.popup).find(':file');

		// clear previously selected file and url
        $file.val('');
        $iframe.contents().find('body').html('');
        $existing.attr('value', '');

        $('.browser-tabs a:first').tab('show');
		var selected_image = "#url"; //$('.browser-tabs li.active').attr('href');
        $('.browser-tabs a[data-toggle="tab"]').on('shown', function(e) {
            selected_image = $(e.target).attr('href');
        });
        
        $(data.popup).find('.save-image').unbind('click').bind('click', function(e) {
            if (selected_image == '#existing') {
                var existing = $(data.popup).find('iframe[name="existing"]').contents().find('.selected-size').val();
                if (existing != 'undefined') {
                    editor.execCommand(data.command, existing, null, data.button);
                    closePopup(editor);                    
                }
            } else if(selected_image == '#upload' && $file.val() != '') { // proceed if any file was selected
                $iframe.bind('load', function() {
                    try {
                        var file_url = $iframe.contents().find("pre").html();
                    } catch(e) {};
                    if(file_url) {
                        var obj = $.parseJSON(file_url).image;
                        editor.execCommand(data.command, obj, null, data.button);
                    } else {
                        alert('An error occured during upload!');
                    }
                    $iframe.unbind('load');
                    closePopup(editor);
                });
                $(data.popup).find('form').attr('action', $.cleditor.buttons.image.uploadUrl).submit();
            } else if (selected_image == '#url' && $text.val() != '') {
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
            
        $('.browser-url-tabs a:first').tab('show');
		var selected_url = "#link-url"; //$('.browser-url-tabs li.active').attr('href');
        $('.browser-url-tabs a[data-toggle="tab"]').on('shown', function (e) {
            selected_url = $(e.target).attr('href');
        })        
        $(data.popup).find('.save-link').unbind('click').bind('click', function(e) {            
            $existing = $(data.popup).find('iframe[name="existing"]').contents().find('.url').val();
            if (selected_url == '#existing-url' && $existing != undefined) {
                editor.execCommand(data.command, $existing, $existing, data.button);
                closePopup(editor);
            } else if (selected_url == '#link-url' && $text.val()) {
                editor.execCommand(data.command, $text.val(), $text.val(), data.button);
                closePopup(editor);
            }            
            return false;
        });
	}
})(jQuery);
