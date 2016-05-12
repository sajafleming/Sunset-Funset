$(document).ready(function () {

    function initialize() {
      var mapProp = {
        center:new google.maps.LatLng(37.7749,-122.4194),
        zoom:10,
        mapTypeId:google.maps.MapTypeId.ROADMAP
      };
      var map=new google.maps.Map(document.getElementById("googleMap"),mapProp);
      
      var geocoder = new google.maps.Geocoder();

      document.getElementById('submit-location').addEventListener('click', function() {

        geocodeAddress(geocoder, map);
      });
    }
    google.maps.event.addDomListener(window, 'load', initialize);

    // var xmlhttp = new XMLHttpRequest();
    // xmlhttp.open("GET", "https://maps.googleapis.com/maps/api/place/textsearch/output?tacobell")
    // xmlhttp.send()
    // console.log(xhr.statusText)
  
    function geocodeAddress(geocoder, resultsMap) {
      console.log('hi!')
      var address = document.getElementById('user-location').value;
      geocoder.geocode({'address': address}, function(results, status) {
        console.log(results)
        if (status === google.maps.GeocoderStatus.OK) {
          resultsMap.setCenter(results[0].geometry.location);
        // ajax call to get the places where markers should be based on location

          // put inside success function
          var marker = new google.maps.Marker({
            map: resultsMap,
            position: results[0].geometry.location
          });
        }  else {
          alert('Geocode was not successful for the following reason: ' + status);
        }
      });
    }


});