//loading the 'login' angularJS module
//angular.module('CustomFilter').controller('followBtnCtrl', function($scope) {
var fba = angular.module('custStatApp', []);
//defining the login controller
fba.controller('custStatCtrl', function($scope, $http) {


	$scope.actcust = function() {
		//alert("SSS"+arguments[0]);
		//confirm("Do you want to pay "+arguments[0]);
		alert("Paying, Please Wait");
        
		document.getElementById(arguments[0]).style.display = "block";
		document.getElementById('button_'+arguments[0]).style.display = "none";
		
		$http({
			method : "POST",
			url : '/mybillpayment',
			data : {
				"billing_id" : arguments[0]
			}
		}).success(function(data) {
			
			//checking the response data for statusCode
			if (data.statusCode == 200) {
				
			}
			else{
				
			}
				//Making a get call to the '/redirectToHomepage' API
				//window.location.assign("/"); 
		}).error(function(error) {
			$scope.unexpected_error = false;
			$scope.username_email_exists = true;
		});
		
	};



});

