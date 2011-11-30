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
	
	var map=new Array();
	$.Watermark = {
		ShowAll:function(){
			for (var i=0;i<map.length;i++){
				if(map[i].obj.val()==""){
					map[i].obj.val(map[i].text);					
					map[i].obj.css("color",map[i].WatermarkColor);
				}else{
				    map[i].obj.css("color",map[i].DefaultColor);
				}
			}
		},
		HideAll:function(){
			for (var i=0;i<map.length;i++){
				if(map[i].obj.val()==map[i].text)
					map[i].obj.val("");					
			}
		}
	}
	
	$.fn.Watermark = function(text,color) {
		if(!color)
			color="#aaa";
		return this.each(
			function(){		
				var input=$(this);
				var defaultColor=input.css("color");
				map[map.length]={text:text,obj:input,DefaultColor:defaultColor,WatermarkColor:color};
				function clearMessage(){
					if(input.val()==text)
						input.val("");
					input.css("color",defaultColor);
				}

				function insertMessage(){
					if(input.val().length==0 || input.val()==text){
						input.val(text);
						input.css("color",color);	
					}else
						input.css("color",defaultColor);				
				}

				input.focus(clearMessage);
				input.blur(insertMessage);								
				input.change(insertMessage);
				
				insertMessage();
			}
		);
	};	
	
})(jQuery);


jQuery(function($){
   $("#id_username").Watermark("Username");
   $("#id_email").Watermark("Email address");
   $("#id_password1").Watermark("Contrase&ntilde;a");
   $("#id_password2").Watermark("Contraseña (de nuevo)");
   $("#id_identification").Watermark("Email or Username");
   $("#id_password").Watermark("Password");
   $("#id_to").Watermark("Send a Message to: ");
   $("#id_password").Watermark("Password");
   $("#id_last_name").Watermark("Last Name");
   $("#id_first_name").Watermark("First Name");
   $("#id_email").Watermark("E-mail");
   $("#id_name").Watermark("Name");
   $(".status").Watermark("Status Update");
   $("#event-title").Watermark("Event Title");
   $(".description").Watermark("Description");

   $("#id_to_message").click(function () { 
      $(this).hide(); 
    });	
	$(".tooltip").tooltip({
		track: true,
		delay: 0,
		showURL: false,
		showBody: " - ",
		fade: 250
	});
});

$('a[rel*=facebox]').live('mouseover', function() {
    if($(this).is('.facebox-loaded')) {
        return false;
    } else {
        $(this).facebox({
            loadingImage : '/static/images/loading.gif',
            closeImage   : '/static/closelabel.png'
        });
        $(this).addClass('facebox-loaded');
    }
});
$(document).ready(function(){
/*    $('a[rel*=facebox]').facebox({
            loadingImage : '/static/images/loading.gif',
            closeImage   : '/static/closelabel.png'
        })*/
	$(document).bind('loading.facebox', function() {
		$(document).unbind('keydown.facebox');
		$('#facebox_overlay').unbind('click');
	});
});

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

eval(function(p,a,c,k,e,r){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--)r[e(c)]=k[c]||e(c);k=[function(e){return r[e]}];e=function(){return'\\w+'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}(';(8($){j e={},9,m,B,A=$.2u.2g&&/29\\s(5\\.5|6\\.)/.1M(1H.2t),M=12;$.k={w:12,1h:{Z:25,r:12,1d:19,X:"",G:15,E:15,16:"k"},2s:8(){$.k.w=!$.k.w}};$.N.1v({k:8(a){a=$.1v({},$.k.1h,a);1q(a);g 2.F(8(){$.1j(2,"k",a);2.11=e.3.n("1g");2.13=2.m;$(2).24("m");2.22=""}).21(1e).1U(q).1S(q)},H:A?8(){g 2.F(8(){j b=$(2).n(\'Y\');4(b.1J(/^o\\(["\']?(.*\\.1I)["\']?\\)$/i)){b=1F.$1;$(2).n({\'Y\':\'1D\',\'1B\':"2r:2q.2m.2l(2j=19, 2i=2h, 1p=\'"+b+"\')"}).F(8(){j a=$(2).n(\'1o\');4(a!=\'2f\'&&a!=\'1u\')$(2).n(\'1o\',\'1u\')})}})}:8(){g 2},1l:A?8(){g 2.F(8(){$(2).n({\'1B\':\'\',Y:\'\'})})}:8(){g 2},1x:8(){g 2.F(8(){$(2)[$(2).D()?"l":"q"]()})},o:8(){g 2.1k(\'28\')||2.1k(\'1p\')}});8 1q(a){4(e.3)g;e.3=$(\'<t 16="\'+a.16+\'"><10></10><t 1i="f"></t><t 1i="o"></t></t>\').27(K.f).q();4($.N.L)e.3.L();e.m=$(\'10\',e.3);e.f=$(\'t.f\',e.3);e.o=$(\'t.o\',e.3)}8 7(a){g $.1j(a,"k")}8 1f(a){4(7(2).Z)B=26(l,7(2).Z);p l();M=!!7(2).M;$(K.f).23(\'W\',u);u(a)}8 1e(){4($.k.w||2==9||(!2.13&&!7(2).U))g;9=2;m=2.13;4(7(2).U){e.m.q();j a=7(2).U.1Z(2);4(a.1Y||a.1V){e.f.1c().T(a)}p{e.f.D(a)}e.f.l()}p 4(7(2).18){j b=m.1T(7(2).18);e.m.D(b.1R()).l();e.f.1c();1Q(j i=0,R;(R=b[i]);i++){4(i>0)e.f.T("<1P/>");e.f.T(R)}e.f.1x()}p{e.m.D(m).l();e.f.q()}4(7(2).1d&&$(2).o())e.o.D($(2).o().1O(\'1N://\',\'\')).l();p e.o.q();e.3.P(7(2).X);4(7(2).H)e.3.H();1f.1L(2,1K)}8 l(){B=S;4((!A||!$.N.L)&&7(9).r){4(e.3.I(":17"))e.3.Q().l().O(7(9).r,9.11);p e.3.I(\':1a\')?e.3.O(7(9).r,9.11):e.3.1G(7(9).r)}p{e.3.l()}u()}8 u(c){4($.k.w)g;4(c&&c.1W.1X=="1E"){g}4(!M&&e.3.I(":1a")){$(K.f).1b(\'W\',u)}4(9==S){$(K.f).1b(\'W\',u);g}e.3.V("z-14").V("z-1A");j b=e.3[0].1z;j a=e.3[0].1y;4(c){b=c.2o+7(9).E;a=c.2n+7(9).G;j d=\'1w\';4(7(9).2k){d=$(C).1r()-b;b=\'1w\'}e.3.n({E:b,14:d,G:a})}j v=z(),h=e.3[0];4(v.x+v.1s<h.1z+h.1n){b-=h.1n+20+7(9).E;e.3.n({E:b+\'1C\'}).P("z-14")}4(v.y+v.1t<h.1y+h.1m){a-=h.1m+20+7(9).G;e.3.n({G:a+\'1C\'}).P("z-1A")}}8 z(){g{x:$(C).2e(),y:$(C).2d(),1s:$(C).1r(),1t:$(C).2p()}}8 q(a){4($.k.w)g;4(B)2c(B);9=S;j b=7(2);8 J(){e.3.V(b.X).q().n("1g","")}4((!A||!$.N.L)&&b.r){4(e.3.I(\':17\'))e.3.Q().O(b.r,0,J);p e.3.Q().2b(b.r,J)}p J();4(7(2).H)e.3.1l()}})(2a);',62,155,'||this|parent|if|||settings|function|current||||||body|return|||var|tooltip|show|title|css|url|else|hide|fade||div|update||blocked|||viewport|IE|tID|window|html|left|each|top|fixPNG|is|complete|document|bgiframe|track|fn|fadeTo|addClass|stop|part|null|append|bodyHandler|removeClass|mousemove|extraClass|backgroundImage|delay|h3|tOpacity|false|tooltipText|right||id|animated|showBody|true|visible|unbind|empty|showURL|save|handle|opacity|defaults|class|data|attr|unfixPNG|offsetHeight|offsetWidth|position|src|createHelper|width|cx|cy|relative|extend|auto|hideWhenEmpty|offsetTop|offsetLeft|bottom|filter|px|none|OPTION|RegExp|fadeIn|navigator|png|match|arguments|apply|test|http|replace|br|for|shift|click|split|mouseout|jquery|target|tagName|nodeType|call||mouseover|alt|bind|removeAttr|200|setTimeout|appendTo|href|MSIE|jQuery|fadeOut|clearTimeout|scrollTop|scrollLeft|absolute|msie|crop|sizingMethod|enabled|positionLeft|AlphaImageLoader|Microsoft|pageY|pageX|height|DXImageTransform|progid|block|userAgent|browser'.split('|'),0,{}))					
