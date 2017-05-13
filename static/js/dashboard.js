$(function(){
	$('#createInstance').click(function(){

		$.ajax({
			url: '/createInstance',
			type: 'POST',
			success: function(response){
				$("#result").html("<b>Instance created successfully</b>");
				$("#ip").html("IP address of instance is :"+response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});
