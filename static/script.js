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
      document.getElementById('user-location').addEventListener('submit', function() {
        geocodeAddress(geocoder, map);
      });


      // bias search results toward area
      var defaultBounds = new google.maps.LatLngBounds(
        // new google.maps.LatLng(37.1, -95.7)
        new google.maps.LatLng(37.1, -95.7));

      var options = {
        bounds: defaultBounds
      }

      // Get the HTML input element for the autocomplete search box
      var input = document.getElementById('user-location');
      //google.maps.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

      // Create the autocomplete object
      var autocomplete = new google.maps.places.Autocomplete(input, options);
    }
    google.maps.event.addDomListener(window, 'load', initialize);

  
    function geocodeAddress(geocoder, resultsMap) {
      console.log('hi!')
      var address = document.getElementById('user-location').value;
      geocoder.geocode({'address': address}, function(results, status) {
        console.log(results)
        if (status === google.maps.GeocoderStatus.OK) {
          resultsMap.setCenter(results[0].geometry.location);
        // ajax call to get the places where markers should be based on location

          console.log("Lat " + results[0].geometry.location.lat());
          console.log("Lng " + results[0].geometry.location.lng());

          lat = results[0].geometry.location.lat()
          lng = results[0].geometry.location.lng()

          // Do ajax request with lat and lng
          $.ajax({
            url: "sunset-spots?lat=" + lat + "&lng=" + lng,
            success: plotSunsetSpots,
            dataType: "json"
          });

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

    function plotSunsetSpots(data) {
      // data is a dictionary equal to what your /sunset-spots route constructed
      console.log(data)
      // pull out top sunset spots

      // for each top sunset spot, add a marker to the map
    }
});


// var input = document.getElementById('pac-input');
// var options = {
//   componentRestrictions: {country: 'us'}
// };

// // Create the autocomplete object
// var autocomplete = new google.maps.places.Autocomplete(input, options);




// Bias the autocomplete object to the user's geographical location,
// as supplied by the browser's 'navigator.geolocation' object.
// function geolocate() {
//   if (navigator.geolocation) {
//     navigator.geolocation.getCurrentPosition(function(position) {
//       var geolocation = {
//         lat: position.coords.latitude,
//         lng: position.coords.longitude
//       };
//       var circle = new google.maps.Circle({
//         center: geolocation,
//         radius: position.coords.accuracy
//       });
//       autocomplete.setBounds(circle.getBounds());
//     });
//   }
// }