function plotGraph(data){
	console.log("in plot data");
	var data = [
  {
    x: ['2013-10-04 22:23:00', '2013-11-04 22:23:00', '2013-12-04 22:23:00'],
    y: [1, 3, 6],
    type: 'scatter'
  }
	];

Plotly.newPlot('myPlotDiv', data);
}


(function ($) {
    "use strict"; // Start of use strict
    $(document).ready(function () {
        // Highlight the top nav as scrolling occurs
        
		//$('#networkDetails').hide();
        // Initialize and Configure Scroll Reveal Animation
        
        // On click of button "Plan My Trip" collects information from server about best route ,Uber and Lyft prives and shows visualization		
        /*$('a[id^="network_"]').click(function () {
            console.log("Inside plan trip button function");

            // On button click show the div meant for visualization
            $('#networkDetails').show();
			
			$.ajax({
              type: "GET",
              url: "/getSensors/", 
			  	
              success: function(data) {
                  console.log("success");
				  console.log(data);
				  plotGraph(data);
              }
            });
			*/
			
			/*//creating user data in json format to be used for the google optimized route api
			var origin = $("#start").val();
			var destination = $("#end").val();
			var waypoints =[];
			$("input[id^=vialocation]").each(function() {
				waypoints.push($(this).val());
			});
			var inData =[{"origin":origin,"destination":destination,"waypoints":waypoints}];			
			$.ajax({
				 type: "POST",
				 url: "http://localhost:5000/fetchPrices",
				 data: JSON.stringify(inData),
				 contentType: "application/json",
				 dataType: "json",
				 beforeSend: function(){
					// Show image container
					$("#loader").show();
				 },
				 success: function (data, status, jqXHR) {
					console.log("success");            
					var places = data[0].places;
					var uberPrice = data[0].uberPrice;
					var lyftPrice = data[0].lyftPrice;
					var locationLatLng = data[0].locationLatLng;
					plotMap(locationLatLng);
					plotChart(uberPrice,lyftPrice);
					plotDirections(places);
				},
				complete:function(data){
                   // Hide image container
                    $("#loader").hide();
                },
				 error: function (jqXHR, status) {
						console.log(status);
					  // error handler
					  //console.log("failure:"+ status);
				 }
			});
		*/
			/*$.post("http://localhost:5000/fetchPrices",JSON.stringify(inData),
			function(data, status){
        console.log(data);
			});*/
		
        

        //Add Content Here

    });
})(jQuery);
