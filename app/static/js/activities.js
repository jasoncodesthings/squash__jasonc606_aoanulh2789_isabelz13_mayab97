function init(n, p, a) {
	var num_val_options = n;
	var price_options = p;
	var accessibility_options = a;

	var num_slider = document.getElementById("num_val");
	var num_output = document.getElementById("ppl");
	var num_cur = Number(num_slider.value);
	num_output.innerHTML = num_val_options[num_cur]; // Display the default slider value
					
	// Update the current slider value (each time you drag the slider handle)
	num_slider.oninput = function() {
		var ind = Number(this.value);
		num_output.innerHTML = num_val_options[ind];
	} 
				
					
	var prate_slider = document.getElementById("price");
	var prate_output = document.getElementById("prate");
	var prate_cur = Number(prate_slider.value);
	prate_output.innerHTML = price_options[prate_cur]; // Display the default slider value
					
	// Update the current slider value (each time you drag the slider handle)
	prate_slider.oninput = function() {
		var ind = Number(this.value);
		prate_output.innerHTML = price_options[ind];
	} 
					

	var acc_slider = document.getElementById("accessibility");
	var acc_output = document.getElementById("acc");
	var acc_cur = Number(acc_slider.value);
	acc_output.innerHTML = accessibility_options[acc_cur]; // Display the default slider value
					
	// Update the current slider value (each time you drag the slider handle)
	acc_slider.oninput = function() {
		var ind = Number(this.value);
		acc_output.innerHTML = accessibility_options[ind];
	} 
}