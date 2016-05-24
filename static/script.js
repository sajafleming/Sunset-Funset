$(document).ready(function () {

    // do not need to initialize since I have it wrapped in function ready
    // function initialize() {

    var mapProp = {
      center:new google.maps.LatLng(37.7749,-122.4194),
      zoom:10,
      mapTypeId:google.maps.MapTypeId.ROADMAP

    };

    var map = new google.maps.Map(document.getElementById("googleMap"),mapProp);

    // playing with map styling
      map.set('styles', [
        {
          featureType: 'water',
          elementType: 'geometry',
          stylers: [
            { color: '#a3d2fe' },
            { weight: 1.6 }
          ]
        }, {
          featureType: "road.highway",
          elementType: "geometry",
          stylers: [
            { color: "#fbe87d" },
            { weight: 1 }
          ]
        }, { 
          featureType: "landscape", 
          elementType: "geometry", 
          stylers: [ 
            { hue: "#eceae4" }, 
          ] 
        } 
      ]); 
    
    var geocoder = new google.maps.Geocoder();

    // TODO: rewrite in jquery
    document.getElementById('user-input-form').addEventListener('submit', function(evt) {
      evt.preventDefault()
      geocodeAddress(geocoder, map);
    });
    document.getElementById('user-location').addEventListener('submit', function(evt) {
      geocodeAddress(geocoder, map);
    });

    // Get the HTML input element for the autocomplete search box
    var input = document.getElementById('user-location');
    //google.maps.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

    // Create the autocomplete object
    var autocomplete = new google.maps.places.Autocomplete(input, options);

    // Add event listener for when someone types in the text box
    google.maps.event.addListener(autocomplete, "place_changed", function(evt) {
      geocodeAddress(geocoder, map);
    });

    // Bias the autocomplete object to the user's geographical location,
    // as supplied by the browser's 'navigator.geolocation' object.
    function geolocate() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
          var geolocation = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          };
          var circle = new google.maps.Circle({
            center: geolocation,
            radius: position.coords.accuracy
          });
          autocomplete.setBounds(circle.getBounds());
        });
      }
    }    

    function geocodeAddress(geocoder, resultsMap) {
      console.log('hi!')
      var address = document.getElementById('user-location').value;
      geocoder.geocode({'address': address}, function(results, status) {
        console.log(results)
        if (status === google.maps.GeocoderStatus.OK) {
          resultsMap.setCenter(results[0].geometry.location);
        // ajax call here to get the places where markers should be based on location

          // this is added to get latlong
          console.log("Lat " + results[0].geometry.location.lat());
          console.log("Lng " + results[0].geometry.location.lng());

          lat = results[0].geometry.location.lat()
          lng = results[0].geometry.location.lng()

          // Do ajax request with lat and lng
          // $.ajax({
          //   url: "sunset-spots?lat=" + lat + "&lng=" + lng,
          //   success: plotSunsetSpots,
          //   dataType: "json"
          // });

          // get the lat and long that the user entered and the radius
          var params = {"lat": lat, "lng": lng, 
            "radio": $('input[name=radius]:checked').val()};
          $.get("/sunset-spots", params, plotSunsetSpots);

          // put inside success function
          var marker = new google.maps.Marker({
            map: resultsMap,
            position: results[0].geometry.location
          });

        } else {
          alert('Geocode was not successful for the following reason: ' + status);
          }
    });
  }

      // function to plot the returned sunset spot data
      function plotSunsetSpots(data) {
        // data is a dictionary equal to what the /sunset-spots route constructed
        // pull out top sunset spots
        // console.log(data);
        var sunsetCoordinates = data.results;
        // console.log(sunsetCoordinates);

        length = sunsetCoordinates.length;
        
        for (var i = 0; i < length - 1; i++) {
          console.log(sunsetCoordinates[i][0], sunsetCoordinates[i][1]);

          var myLatLng = {lat: sunsetCoordinates[i][0], lng: sunsetCoordinates[i][1]};

          // var marker = new google.maps.Marker({
          //     map: this.map,
          //     position: myLatLng
          //   });

          addMarker(myLatLng);
        }
      }

    function addMarker(myLatLng) {

      console.log(myLatLng);
      console.log(map);

      // sun image

      // fix location of this pin
      // var icon = {
      // url: "http://oi63.tinypic.com/2b8sv6.jpg", // url
      // scaledSize: new google.maps.Size(100, 100), // scaled size
      // origin: new google.maps.Point(50, 50), // origin
      // anchor: new google.maps.Point(50, 50) // anchor
      // };

      // below didn't work
      // var image = {
      // url: "http://oi63.tinypic.com/2b8sv6.jpg" ,
      // size: new google.maps.Size(200, 300),
      // origin: new google.maps.Point(0, 0),
      // anchor: new google.maps.Point(0, 32),
      // scaledSize: new google.maps.Size(10, 10)
      // };

      // var image = "http://oi63.tinypic.com/2b8sv6.jpg"       
      var marker = new google.maps.Marker({
              position: myLatLng,
              map: map,
              // icon: icon
      });
    }


});



