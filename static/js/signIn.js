$(function(){
	$('#btnSignIn').click(function(){

		$.ajax({
			url: '/signIn',
			data: $('form').serialize(),
			type: 'POST',
			success: function(data){
				if (data!='incorrect'){
					$("#result").html("");
					window.location = data;
					console.log("success login");
				} else {
					$("#result").html("<b>User name or password incorrect</b>");
				}
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});
