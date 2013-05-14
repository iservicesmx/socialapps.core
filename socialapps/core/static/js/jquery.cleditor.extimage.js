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
	};
	
	$.cleditor.buttons.link = {
		name: 'link',
		title: 'Insert Hyperlink,',
		command: 'createlink',
		popupName: 'ext-url',
		popupClass: 'cleditorPrompt',
		stripIndex: $.cleditor.buttons.link.stripIndex,		
		buttonClick: urlButtonClick
	};

    $.cleditor.buttons.multimedia = {
        name: 'multimedia',
        title: 'Insert Multimedia,',
        image: 'multimedia.gif',
        command: 'inserthtml',
        popupName: 'ext-mult',
        popupClass: 'cleditorPrompt',
        buttonClick: multimediaButtonClick
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
            var base = window.location.href.substring(0, window.location.href.lastIndexOf("/") + 1);
            selected_image = $(e.target).attr("href").replace(base, "");
        });

        $(data.popup).find('.save-image').unbind('click').bind('click', function(e) {
            if (selected_image == '#existing') {
                var existing = $(data.popup).find('iframe[name="existing"]').contents().find('.selected-size').val();
                if (existing != 'undefined') {
                    $.get(existing, function(dat) {
                        if (dat.success === true) {
                            editor.execCommand(data.command, dat.thumb_url, null, data.button);
                            closePopup(editor);
                        }
                    });
                }
            } else if(selected_image == '#upload' && $file.val() != '') { // proceed if any file was selected
                var image = $('.selected-size').val();
                if(image) {
                    $.get(image, function(dat) {
                        if (dat.success === true) {
                            $('#upload form').show();
                            $('#upload .data').html(''); 
                            editor.execCommand(data.command, dat.thumb_url, null, data.button);
                            closePopup(editor);
                        }
                    });
                }
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
                var value = '<a href="' + $text.val() + '" target="_blank">' + editor.selectedText() + '</a>';
                editor.execCommand('inserthtml', value, null, data.button);
                closePopup(editor);
            }            
            return false;
        });
	}

    function multimediaButtonClick(e, data) {
        var editor = data.editor,
            $existing = $(data.popup).find('iframe[name="existing"]').contents().find('.url'), html = '';
            $(data.popup).find('.save-multimedia').unbind('click').bind('click', function(e) {
            $existing = $(data.popup).find('iframe[name="existing"]').contents().find('.url').val();
            var mimetype = $(data.popup).find('iframe[name="existing"]').contents().find('.mimetype').html();
            if ($existing != undefined) {
                if(mimetype) {
                    if (mimetype == 'video' || mimetype == 'audio') {
                        var mult_url = $(data.popup).find('iframe[name="existing"]').contents().find('.mult_url').val();
                        var mult_true_type = $(data.popup).find('iframe[name="existing"]').contents().find('.mult_true_type').val();
                        var player_width = 560;
                        var player_height = 315;
                        if(mimetype == 'audio') {
                            player_height = 30;
                        }
                        html = '<video data-setup="" class="video-js vjs-default-skin vjs-tech" controls preload="none" width="'+player_width+'" height="'+player_height+'"><source src="'+ mult_url+'" type="'+ mult_true_type+'"></video>';
                    }
                } else {
                    var img = $(data.popup).find('iframe[name="existing"]').contents().find('.icon').attr('src');
                    html = '<a href="'+ $existing +'"><img src="'+ img +'" /></div>';
                }
                editor.execCommand(data.command, html, null, data.button);
                closePopup(editor);
            }
            return false;
        });
    }
})(jQuery);