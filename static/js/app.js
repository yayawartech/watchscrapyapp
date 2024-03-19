/**
 * Nothing here yet. Add some stuff?
 */
 $(function () {
  $('[data-toggle="tooltip"]').tooltip();
  enableSearchOption();
})

$(function() {
	$("#pills-gold-tab").click(function(){
		populate_gold_data();
	});
	$("#pills-goldsub-tab").click(function(){
		populate_gold_data();
	});

	$("#select_goldk").change(function(){
		populate_gold_data();
	});

	$("#custom_gold").change(function(){
		populate_gold_data();
	});
	

	function populate_gold_data(){
		gold_carat = $( "#select_goldk option:selected" ).text();
		gold_gram = $("#gold_gram").text()
		percentage = $("#custom_gold").val()
	  	$.ajax(
	  		{
	  		url: "/gold/gold_data/"+gold_carat+"/"+gold_gram+"/"+percentage,
	  		success: function(result){

	    		dollar_0 = result[0][0]
	    		usdollar_0 = result[0][1]
	    		$("#dollar_0").text(dollar_0)
	    		$("#usdollar_0").text(usdollar_0)

	    		dollar_5 = result[1][0]
	    		usdollar_5 = result[1][1]
	    		$("#dollar_5").text(dollar_5)
	    		$("#usdollar_5").text(usdollar_5)

	    		dollar_10 = result[2][0]
	    		usdollar_10 = result[2][1]
				$("#dollar_10").text(dollar_10)
	    		$("#usdollar_10").text(usdollar_10)

	    		dollar_15 = result[3][0]
	    		usdollar_15 = result[3][1]
				$("#dollar_15").text(dollar_15)
	    		$("#usdollar_15").text(usdollar_15)

	    		gold_dollar_custom = result[4][0]
	    		gold_usdollar_custom = result[4][1]
				$("#gold_dollar_custom").text(gold_dollar_custom)
	    		$("#gold_usdollar_custom").text(gold_usdollar_custom)
	    		
	    		dollar_24k = result['24k'][0]
	    		usdollar_24k = result['24k'][1]
	    		$("#dollar_24k").text(dollar_24k)
	    		$("#usdollar_24k").text(usdollar_24k)
	  		}
	  	});
	}
})

$(function() {
	$("#pills-platinumsub-tab").click(function(){
		populate_platinum_data();
	});
	$("#custom_platinum").change(function(){
		populate_platinum_data();
	});

	function populate_platinum_data(){
		platinum_gram = $("#platinum_gram").text()
		percentage = $("#custom_platinum").val()
	  	$.ajax(
	  		{
	  		url: "/gold/platinum_data/"+platinum_gram+"/"+percentage,
	  		success: function(result){

	  			platinum_bp_thousand = result["platinum_bp"]
	  			$("#platinum_bp_thousand").text(platinum_bp_thousand);

	    		p_dollar_0 = result[0][0]
	    		p_usdollar_0 = result[0][1]
	    		$("#p_dollar_0").text(p_dollar_0)
	    		$("#p_usdollar_0").text(p_usdollar_0)

	    		p_dollar_5 = result[1][0]
	    		p_usdollar_5 = result[1][1]
	    		$("#p_dollar_5").text(p_dollar_5)
	    		$("#p_usdollar_5").text(p_usdollar_5)

	    		p_dollar_10 = result[2][0]
	    		p_usdollar_10 = result[2][1]
				$("#p_dollar_10").text(p_dollar_10)
	    		$("#p_usdollar_10").text(p_usdollar_10)

	    		p_dollar_15 = result[3][0]
	    		p_usdollar_15 = result[3][1]
				$("#p_dollar_15").text(p_dollar_15)
	    		$("#p_usdollar_15").text(p_usdollar_15)

	    		platinum_dollar_custom = result[4][0]
	    		platinum_usdollar_custom = result[4][1]
				$("#platinum_dollar_custom").text(platinum_dollar_custom)
	    		$("#platinum_usdollar_custom").text(platinum_usdollar_custom)
	    		
	    		p_dollar_1000 = result['1000'][0]
	    		p_usdollar_1000 = result['1000'][1]
	    		$("#p_dollar_1000").text(p_dollar_1000)
	    		$("#p_usdollar_1000").text(p_usdollar_1000)
	  		}
	  	});
	}
})

$(function() {
	$("#pills-silversub-tab").click(function(){
		populate_silver_data();
	});

	$("#select_silver").change(function(){
		populate_silver_data();
	});

	$("#custom_silver").change(function(){
		populate_silver_data();
	});
	

	function populate_silver_data(){
		silver_carat = $( "#select_silver option:selected" ).text();
		silver_gram = $("#silver_gram").text()
		percentage = $("#custom_silver").val()
	  	$.ajax(
	  		{
	  		url: "/gold/silver_data/"+silver_carat+"/"+silver_gram+"/"+percentage,
	  		success: function(result){

	    		s_dollar_0 = result[0][0]
	    		s_usdollar_0 = result[0][1]
	    		$("#s_dollar_0").text(s_dollar_0)
	    		$("#s_usdollar_0").text(s_usdollar_0)

	    		s_dollar_5 = result[1][0]
	    		s_usdollar_5 = result[1][1]
	    		$("#s_dollar_5").text(s_dollar_5)
	    		$("#s_usdollar_5").text(s_usdollar_5)

	    		s_dollar_10 = result[2][0]
	    		s_usdollar_10 = result[2][1]
				$("#s_dollar_10").text(s_dollar_10)
	    		$("#s_usdollar_10").text(s_usdollar_10)

	    		s_dollar_15 = result[3][0]
	    		s_usdollar_15 = result[3][1]
				$("#s_dollar_15").text(s_dollar_15)
	    		$("#s_usdollar_15").text(s_usdollar_15)

	    		silver_dollar_custom = result[4][0]
	    		silver_usdollar_custom = result[4][1]
				$("#silver_dollar_custom").text(silver_dollar_custom)
	    		$("#silver_usdollar_custom").text(silver_usdollar_custom)
	    		
	    		s_dollar_999 = result['999'][0]
	    		s_usdollar_999 = result['999'][1]
	    		$("#s_dollar_999").text(s_dollar_999)
	    		$("#s_usdollar_999").text(s_usdollar_999)
	  		}
	  	});
	}
})


$(function() {
	$body = $("body");

	$(document).on({
    	ajaxStart: function() { $body.addClass("loading");    },
     	ajaxStop: function() { $body.removeClass("loading"); }    
	});

	$("#fetch-now").click(function(){
		fetch_data_load();
	});

	function fetch_data_load(){
		$.ajax(
	  		{
	  		url: "/gold/fetchNow/",
	  		success: function(result){
	  			$("#gold_price").text(result['gold_price']);
	  			$("#gold_weight").text(result['gold_weight']);
	  			$("#platinum_weight").text(result['platinum_weight']);
	  			$("#silver_weight").text(result['silver_weight']);
	  			$("#last_updated").text(result['last_updated']);
	  		}
	  	});
	}
})

$(function () {
	$(".tab-d").click(function(){
		$(".tab-d").each(function() {
       		$(this).find("span").removeClass("badge-secondary");
     	});
		
		$(this).find("span").addClass("badge-secondary");
	});
	var $swipeTabsContainer = $('.swipe-tabs'),
		$swipeTabs = $('.swipe-tab'),
		$swipeTabsContentContainer = $('.swipe-tabs-container'),
		currentIndex = 0,
		activeTabClassName = 'active-tab';

	$swipeTabsContainer.on('init', function(event, slick) {
		$swipeTabsContentContainer.removeClass('invisible');
		$swipeTabsContainer.removeClass('invisible');

		currentIndex = slick.getCurrent();
		$swipeTabs.removeClass(activeTabClassName);
       	$('.swipe-tab[data-slick-index=' + currentIndex + ']').addClass(activeTabClassName);
	});

	$swipeTabsContainer.slick({
		//slidesToShow: 3.25,
		slidesToShow: 10,
		slidesToScroll: 1,
		centreMode: true,
		arrows: false,
		infinite: false,
		swipeToSlide: true,
		touchThreshold: 10,
		dots: false,
		  infinite: false,
		  speed: 300,
		  responsive: [
		    {
		      breakpoint: 1024,
		      settings: {
		        slidesToShow: 10,
		        slidesToScroll: 1,
		        infinite: true,
		        dots: false
		      }
		    },
		    {
		      breakpoint: 700,
		      settings: {
		        slidesToShow: 5,
		        slidesToScroll: 1,
		        infinite: true,
		        dots: false
		      }
		    },
		    {
		      breakpoint: 600,
		      settings: {
		        slidesToShow: 5,
		        slidesToScroll: 1
		      }
		    },
		    {
		      breakpoint: 480,
		      settings: {
		        slidesToShow: 3,
		        slidesToScroll: 1
		      }
		    }
		    // You can unslick at a given breakpoint now by adding:
		    // settings: "unslick"
		    // instead of a settings object
		  ]
	});

	$swipeTabsContentContainer.slick({
		asNavFor: $swipeTabsContainer,
		slidesToShow: 1,
		slidesToScroll: 1,
		arrows: false,
		infinite: false,
		swipeToSlide: true,
    	draggable: false,
		touchThreshold: 10
	});


	$swipeTabs.on('click', function(event) {
        // gets index of clicked tab
        currentIndex = $(this).data('slick-index');
        $swipeTabs.removeClass(activeTabClassName);
        $('.swipe-tab[data-slick-index=' + currentIndex +']').addClass(activeTabClassName);
        $swipeTabsContainer.slick('slickGoTo', currentIndex);
        $swipeTabsContentContainer.slick('slickGoTo', currentIndex);
    });

    //initializes slick navigation tabs swipe handler
    $swipeTabsContentContainer.on('swipe', function(event, slick, direction) {
    	currentIndex = $(this).slick('slickCurrentSlide');
		$swipeTabs.removeClass(activeTabClassName);
		$('.swipe-tab[data-slick-index=' + currentIndex + ']').addClass(activeTabClassName);
	});
});