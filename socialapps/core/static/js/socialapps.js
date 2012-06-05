function ctRotatorBridgeLi(container){
  this.container = container;
}

ctRotatorBridgeLi.prototype = {
  getDataSource:function(){
    var dataSource = [];
    this.container.find('li').each(function(){
	  var e = $(this);
	  if(e.children('a').size() == 0){
	    dataSource.push({title:e.text()});
	  }else{
	    e = e.children('a');
	    dataSource.push({title:e.text(), url:e.attr('href')});
	  }
	});
	return dataSource;
  }
};


(function($){
	$.fn.ctRotator = function(dataSource, options){
	  options = $.extend({
	     showCount: 5,
		 speed: 6000, //in milliseconds
		 fadeInSpeed: 750,
		 fadeOutSpeed: 250,
		 fadeEffect: true,
		 useTooltip: false,
		 shuffle: false,
		 itemRenderer: function(item){ 
		   if(item.url == null){
		     return '<li class="ctrotator-item ' + item.type +'"><a class="rotator_item.' + item.id + '" href="' + item.url+ '">' + item.title + '</a><div class="hideSelector"><a class="uiSelectorButton uiCloseButton" href="#" role="button" aria-haspopup="1" title="Eliminar" rel="toggle"></a></div></li>'; 
		   }else{
		     return '<li class="ctrotator-item ' + item.url +'"><a class="rotator_item">' + item.title + '</a></li>'; 
		   } 
		 },
		 tooltipOptions: {}
	  }, options);

	  if(options.showCount < 1){
	    throw('options.showCount must be greater than 0');
	  }

	  return this.each(function(){
	    $(this).empty();
	    doRotating(dataSource, this, options);
	  });
	};

	function doRotating(dataSource, container, options){
	  var rotator = new ctRotatorList(dataSource, options.shuffle);
	  var showCount = options.showCount;
	  for(var i = 0; i < showCount; i++){
	    insertItem(rotator.gotoNext(), container, options);
	  }
	  updateRotation(rotator, container, options);
	}

	function updateRotation(rotator, container, options){
	  var item = rotator.gotoNext();
	  var newLi = insertItem(item, container, options);

	  if(options.fadeEffect){
	    newLi.hide();
		var inSpeed = options.fadeInSpeed;
		var outSpeed = options.fadeOutSpeed;
	      $(container).children(':last').fadeOut(outSpeed, function(){
		    $(this).remove()
			newLi.fadeIn(inSpeed, function(){
		      setTimeout(function(){updateRotation(rotator, container, options)}, options.speed);
	        });
		  });
	  }else{
	    $(container).children(':last').remove();
		setTimeout(function(){updateRotation(rotator, container, options)}, options.speed);
	  }

	}

	function insertItem(item, container, options){
	   var rendered = options.itemRenderer(item);
	   var newLi = $(rendered);
	   if(newLi.size() == 0){
	     newLi = $('<li></li>').append(rendered);
	   }
	   $(container).prepend(newLi);

	   if(options.useTooltip){
	     newLi.tooltip($.extend({
		   fade:50,
		   delay:800,
		   opacity: 1,
		   bodyHandler: function(){
		       return item.tip;
			 }
		 }, options.tooltipOptions));
	   }

	   return newLi;
	}


	function ctRotatorList(list, shuffle){
	  this.cursor = 0;
	  this.list = list;
	  this.shuffle = shuffle == null ? false : shuffle;
	  if(this.shuffle){
	    this.list = this.shuffleArray(this.list);
	  }
	}

	ctRotatorList.prototype = { 
	  gotoNext:function(){
		  if(this.cursor >= this.getCount() - 1){ 
	        this.cursor = 0;
		  }else{
		    this.cursor++;
		  }
	      return this.list[this.cursor];
	  },
	  getCount:function(){
	    return this.list.length;
	  },
	  shuffleArray:function(o){ 
	    for(var j, x, i = o.length; i; j = parseInt(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
	      return o;
	  }
	};
	
	
})(jQuery);


	//tab effects

	var TabbedContent = {
		init: function() {	
			$(".tab_item").mouseover(function() {

				var background = $(this).parent().find(".moving_bg");

				$(background).stop().animate({
					left: $(this).position()['left']
				}, {
					duration: 300
				});

				TabbedContent.slideContent($(this));

			});
		},

		slideContent: function(obj) {

			var margin = $(obj).parent().parent().find(".slide_content").width();
			margin = margin * ($(obj).prevAll().size() - 1);
			margin = margin * -1;

			$(obj).parent().parent().find(".tabslider").stop().animate({
				marginLeft: margin + "px"
			}, {
				duration: 300
			});
		}
	}

	$(document).ready(function() {
		TabbedContent.init();
		$(".toggle_container").css("display","none");	
		$(".toggle_container").hide();	
		$(".messages-all").fadeIn(2000).fadeTo(2000, 1).fadeOut(1000);  
	    $("#message-container").fadeIn(2000).fadeTo(2000, 1).fadeOut(1000);         
        //TODO: What is this for?

        $("header").mouseenter(function(){
            if(typeof timer !== 'undefined') {
                clearTimeout(timer);
            }
            $(".toggle_container").slideDown('fast');
			$(".toggle_container").css("display","block");
			$(".message-alert").hide();
        }).mouseleave(function(){
            timer = setTimeout(function() {
                $(".toggle_container").slideUp('fast');
    			$(".message-alert").fadeIn("slow");
            }, 1000);
        });      

		//$("#page").mouseenter(function(){	
		//	$(".toggle_container").hide("slow");
		//	$(".message-alert").fadeIn("slow");			
        //});
		//$(".container").mouseleave(function(){	});
		$("#header_input").mouseenter(function(){
			$(".toggle_container").css("display","block");
		});
		//$("#aux").mouseleave(function(){	
		//	$(".toggle_container").hide("slow");
		//});


		$("#area-content").click(function(){
      //      $(this).toggleClass("active");//.next();
            $(".media-send").show();
            $("#name").hide();
        });
	});

$(function() {
    $(".form").jqTransform();
});
