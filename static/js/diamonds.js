
/* Functions to calculate diamond prices */
$(function () {

	//1. Baguette
	$(".baguette-input").change(function(){
		vLength = parseFloat($("#baguette-vLength").val())
		hWidth = parseFloat($("#baguette-hWidth").val())
		depth = parseFloat($("#baguette-depth").val())
		if(vLength && hWidth && depth){
			var output = calculate_weight_baguette(vLength,hWidth,depth);
			$("#baguette-result").text(output.toFixed(3));
		}
	});

	function calculate_weight_baguette(v_length,h_length,depth){
		var estimated_weight = v_length * h_length * depth * 0.00915
		return estimated_weight;
	}

	//2. Brilliant
	$(".brilliant-input").change(function(){
		vLength = parseFloat($("#brilliant-vLength").val())
		hWidth = parseFloat($("#brilliant-hWidth").val())
		depth = parseFloat($("#brilliant-depth").val())
		thickness = $("#brilliant-thickness").val()
		if(vLength && hWidth && depth && thickness){
			var output = calculate_weight_brilliant(vLength,hWidth,depth,thickness);
			$("#brilliant-result").text(output.toFixed(3));
		}
	});

	function calculate_weight_brilliant(v_length,h_length,depth,gtf){
		var average_grid_diam = (v_length+h_length)/2;
		var wc = weightCorrector(average_grid_diam,gtf);
		var estimated_weight = average_grid_diam*average_grid_diam * depth * 0.0061*wc;
		return estimated_weight;
	}

	//3. Emerald
	$(".emerald-input").change(function(){
		vLength = parseFloat($("#emerald-vLength").val())
		hLength = parseFloat($("#emerald-hWidth").val())
		depth = parseFloat($("#emerald-depth").val())
		thickness = $("#emerald-thickness").val()
		if(vLength && hLength && depth && thickness){
			var output = emerald_weight_estimation(vLength,hLength,depth,thickness);
			$("#emerald-result").text(output.toFixed(3));
		}
	});

	function emerald_weight_estimation(v_length,h_length,depth,gtf){
		var average_grid_diam = (v_length+h_length)/2;
		var wc = weightCorrector(average_grid_diam,gtf);
		var estimated_weight = v_length * h_length * depth * private_emerald_ajustment(v_length,h_length)*wc
		return estimated_weight;
	}
	
	function private_emerald_ajustment(v_length,h_length){ 
		var min_length= v_length>h_length?h_length:v_length;
		var max_length = v_length>h_length?v_length:h_length;
		var ratio =max_length/min_length;
		if(Math.round(ratio)==1) return 0.0080
		if(Math.round(ratio)==1.5) return 0.00920;
		if(Math.round(ratio)==2) return 0.00100;
		if(Math.round(ratio)==2.5) return 0.00106;

		//If not math i use a Lineal regreation calculated with above data
		return 0.00172*ratio + 0.00644
	}

	//4. European
	$(".european-input").change(function(){
		vLength = parseFloat($("#european-vLength").val())
		hWidth = parseFloat($("#european-hWidth").val())
		depth = parseFloat($("#european-depth").val())
		thickness = $("#european-thickness").val()
		if(vLength && hWidth && depth && thickness){
			var output = calculate_weight_european(vLength,hWidth,depth,thickness);
			$("#european-result").text(output.toFixed(3));
		}
	});

	function calculate_weight_european(v_length,h_width,depth,gtf){
		var average_grid_diam = (v_length+h_width)/2;
		var wc = weightCorrector(average_grid_diam,gtf);
		//var estimated_weight = average_grid_diam*average_grid_diam * depth * 0.0061*wc;
        var estimated_weight = v_length*h_width*depth*0.0064*wc;
		return estimated_weight;
	}

	//5. Marquise
	$(".marquise-input").change(function(){
		vLength = parseFloat($("#marquise-vLength").val())
		hWidth = parseFloat($("#marquise-hWidth").val())
		depth = parseFloat($("#marquise-depth").val())
		thickness = $("#marquise-thickness").val()
		if(vLength && hWidth && depth && thickness){
			var output = calculate_weight_marquise(vLength,hWidth,depth,thickness);
			$("#marquise-result").text(output.toFixed(3));
		}
	});

	function calculate_weight_marquise(v_length,h_length,depth,gtf){
		var average_grid_diam = (v_length+h_length)/2;
		var wc = weightCorrector(average_grid_diam,gtf);
		var estimated_weight = v_length * h_length * depth *private_marquise_ajustment(v_length,h_length)*wc;
		return estimated_weight;
	}
	
	function private_marquise_ajustment(v_length,h_length){ 
		var min_length= v_length>h_length?h_length:v_length;
		var max_length = v_length>h_length?v_length:h_length;
		var ratio =max_length/min_length;
		if(Math.round(ratio)==1.5) return 0.00565;
		if(Math.round(ratio)==2) return 0.00580;
		if(Math.round(ratio)==2.5) return 0.00585;
		if(Math.round(ratio)==3) return 0.00595;

		//If not math i use a Lineal regreation calculated with above data
		return  0.00019*ratio + 0.00539; 
	}

	//6. Oval
	$(".oval-input").change(function(){
		vLength = parseFloat($("#oval-vLength").val())
		hWidth = parseFloat($("#oval-hWidth").val())
		depth = parseFloat($("#oval-depth").val())
		thickness = $("#oval-thickness").val()
		if(vLength && hWidth && depth && thickness){
			var output = calculate_weight_oval(vLength,hWidth,depth,thickness);
			$("#oval-result").text(output.toFixed(3));
		}
	});
	function calculate_weight_oval(v_length,h_length,depth,gtf){
		var average_grid_diam = (v_length+h_length)/2;
		var wc = weightCorrector(average_grid_diam,gtf);
		var estimated_weight = average_grid_diam*average_grid_diam * depth * 0.0062*wc;
		return estimated_weight;
	}

	//7. Pear
	$(".pear-input").change(function(){
		vLength = parseFloat($("#pear-vLength").val())
		hWidth = parseFloat($("#pear-hWidth").val())
		depth = parseFloat($("#pear-depth").val())
		thickness = $("#pear-thickness").val()
		if(vLength && hWidth && depth && thickness){
			var output = calculate_weight_pear(vLength,hWidth,depth,thickness);
			$("#pear-result").text(output.toFixed(3));
		}
	});

	function calculate_weight_pear(v_length,h_length,depth,gtf){
		var average_grid_diam = (v_length+h_length)/2;
		var wc = weightCorrector(average_grid_diam,gtf);
		var estimated_weight = v_length * h_length * depth *private_pear_ajustment(v_length,h_length)*wc;
		return estimated_weight;
	}
	
	function private_pear_ajustment(v_length,h_length){ 
		var min_length= v_length>h_length?h_length:v_length;
		var max_length = v_length>h_length?v_length:h_length;
		var ratio =max_length/min_length;
		if(Math.round(ratio)==1.25) return 0.00615;
		if(Math.round(ratio)==1.5) return 0.00600;
		if(Math.round(ratio)==1.66) return 0.00590;
		if(Math.round(ratio)==2) return 0.00575;

		//If not math i use a Lineal regreation calculated with above data
		return   -0.00053*ratio + 0.00681;
	}
	
	//8. Pear
	$(".princess-input").change(function(){
		vLength = parseFloat($("#princess-vLength").val())
		hWidth = parseFloat($("#princess-hWidth").val())
		depth = parseFloat($("#princess-depth").val())
		thickness = $("#princess-thickness").val()
		if(vLength && hWidth && depth && thickness){
			var output = calculate_weight_princess(vLength,hWidth,depth,thickness);
			$("#princess-result").text(output.toFixed(3));
		}
	});

	function calculate_weight_princess(v_length,h_length,depth,gtf){
		var average_grid_diam = (v_length+h_length)/2;
		var wc = weightCorrector(average_grid_diam,gtf);
		var estimated_weight = v_length * h_length * depth * 0.0083*wc;
		return estimated_weight;
	}

	//9. Baguette
	$(".tapered-input").change(function(){
		tWidth = parseFloat($("#tapered-tWidth").val())
		bWidth = parseFloat($("#tapered-bWidth").val())
		length = parseFloat($("#tapered-length").val())
		depth = parseFloat($("#tapered-depth").val())
		if(tWidth && bWidth && depth && length){
			var output = calculate_weight_tapered(length,tWidth,bWidth,depth);
			$("#tapered-result").text(output.toFixed(3));
		}
	});

	function calculate_weight_tapered(v_length,h_length_top,h_length_bottom,depth){
		var average_horizontal = (h_length_top+h_length_bottom)/2;
		var estimated_weight = v_length * average_horizontal * depth * 0.00915
		return estimated_weight;
	}

	//5. Marquise
	$(".triangle-input").change(function(){
		vLength = parseFloat($("#triangle-vLength").val())
		hWidth = parseFloat($("#triangle-hWidth").val())
		depth = parseFloat($("#triangle-depth").val())
		thickness = $("#triangle-thickness").val()
		if(vLength && hWidth && depth && thickness){
			var output = calculate_weight_triangle(vLength,hWidth,depth,thickness);
			$("#triangle-result").text(output.toFixed(3));
		}
	});

	function calculate_weight_triangle(v_length,h_length,depth,gtf){
		var average_grid_diam = (v_length+h_length)/2;
		var wc = weightCorrector(average_grid_diam,gtf);
		var estimated_weight = v_length*h_length * depth * 0.0057*wc;
		return estimated_weight;
	}

	function weightCorrector(diameter,gtf){
		
		switch (gtf){
	        case "sth":
	            if (diameter<=4.1){
	                return 1.03;
	            }else if(diameter<=6.9){
	                return 1.02;
	            }else{
	                 return 1.01;
	            }
	        break;
	        case "th":
	            if (diameter<=4.65){
	                return 1.04;
	            }else if(diameter<=6.55){
	                return 1.03;
	            }else{
	                 return 1.02;
	            }
	        break;
	        case "vth":
	            if (diameter<=4.15){
	                return 1.09;
	            }else if(diameter<=4.7){
	                return 1.08;
	            }else if(diameter<=5.5){
	                return 1.07;
	            }else if(diameter<=6.55){
	                return 1.06;
	            }else if(diameter<=8.1){
	                return 1.05;
	            }else{
	                return 1.04;
	            }
	        break;
	        case "eth":
	            if (diameter<=4.15){
	                return 1.12;
	            }else if(diameter<=4.55){
	                return 1.11;
	            }else if(diameter<=5.1){
	                return 1.10;
	            }else if(diameter<=5.75){
	                return 1.09;
	            }else if(diameter<=6.55){
	                return 1.08;
	            }else if(diameter<=7.65){
	                return 1.07;
	            }else{
	                return 1.06;
	            }
	        break;
	        case "thm":
	        	return 1.0;
	    }
	}

})
