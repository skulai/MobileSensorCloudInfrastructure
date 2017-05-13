$(function(){
$('#add').click(function(){
  networkName = $("#network").val();
  send = {'userid':1, 'networkName':networkName, 'sensor':selected};
  //alert(JSON.stringify(send))
$.ajax ({
  url: '/addSensor',
  data: JSON.stringify(send, null, '\t'),
  contentType: 'application/json;charset=UTF-8',
  type: 'POST',
  success: function(data){
    $("#result").html("<b>Sensors added successfully. Virtual Sensor Network Created.</b>");
  },
  error: function(error){
    console.log(error);
  }
});
});
});

$(function(){
$('#del').click(function(){
selected = [];
display = [];
document.getElementById("sensorname").innerHTML = "";
});
});


function animateCircle(line) {
    var count = 0;
    window.setInterval(function() {
      count = (count + 1) % 200;

      var icons = line.get('icons');
      icons[0].offset = (count / 2) + '%';
      line.set('icons', icons);
  }, 20);
};
