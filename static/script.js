$(document).ready(function () {

    // do not need to initialize since I have it wrapped in function ready
    // function initialize() {

    var mapProp = {
      center: new google.maps.LatLng(37.7749,-122.4194),
      zoom:10,
      mapTypeId:google.maps.MapTypeId.ROADMAP
    };

    // new google maps object
    var map = new google.maps.Map($("#googleMap")[0], mapProp);
    var markers = [];

    // if geolocation can obtain location from browser, center map on user location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
        initialLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
        map.setCenter(initialLocation);
      });
    }

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
    
    // new google maps geocoder object
    var geocoder = new google.maps.Geocoder();

    // document.getElementById('user-input-form').addEventListener('submit', function(evt) {
    //   evt.preventDefault()
    //   geocodeAddress(geocoder, map);
    // });
    // document.getElementById('user-textbox').addEventListener('submit', function(evt) {
    //   geocodeAddress(geocoder, map);
    // });

    // rewrote above in jquery
    $('#user-input-form').submit(function(evt) {
      evt.preventDefault()
      geocodeAddress(geocoder, map);
    });
    $('#user-textbox').submit(function(evt) {
      geocodeAddress(geocoder, map);
    });

    // need to create a list of markers so I can clear
    // document.getElementById('user-input-form').addEventListener('submit', function(evt) {
    //   while (markers.length > 0) {
    //     markers.pop().setMap(null);
    //   }
    //   markers.length = 0;
    // });

    // Get the HTML input element for the autocomplete search box
    // var input = document.getElementById('user-textbox');
    var input = $('#user-textbox')[0]

    // Create the autocomplete object
    var autocomplete = new google.maps.places.Autocomplete(input);

    // Clears textbox when user starts typing
    $('input:text').focus(function(evt) {
      $(this).val('');
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
      var address = $('#user-textbox').val()
      geocoder.geocode({'address': address}, function(results, status) {
        console.log(results)
        if (status === google.maps.GeocoderStatus.OK) {
          resultsMap.setCenter(results[0].geometry.location);

          // get the latlong from the user's entered location
          console.log("Lat " + results[0].geometry.location.lat());
          console.log("Lng " + results[0].geometry.location.lng());

          lat = results[0].geometry.location.lat()
          lng = results[0].geometry.location.lng()

          // get the lat and long that the user entered and the radius
          var params = {"lat": lat, "lng": lng, 
            "radio": $('input[name=radius]:checked').val()};
          $.get("/sunset-spots", params, plotSunsetSpots);

          // plot the original point
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

        var sunsetPictures = data.pictures;
        var picturesLength = sunsetPictures.length;
        // temp adding pics
        for (var i = 0; i < picturesLength -1; i++) {
          console.log(sunsetPictures[i])

          var pic = data.pictures[i]
          // $('#pictures').html('<img src="' + pic + '"/>');
          $('<img src="' + pic + '"/>').appendTo('#pictures');
        }

        var sunsetCoordinates = data.latlongs;
        var coordinatesLength = sunsetCoordinates.length;
        
        for (var i = 0; i < coordinatesLength - 1; i++) {
          console.log(sunsetCoordinates[i][0], sunsetCoordinates[i][1]);

          var myLatLng = {lat: sunsetCoordinates[i][0], lng: sunsetCoordinates[i][1]};

          addMarker(myLatLng);
        }
      }


      function addMarker(myLatLng) {

        console.log(myLatLng);
        console.log(map);

      // TODO: fix location of this custom pin
      // var icon = {
      // url: "http://oi63.tinypic.com/2b8sv6.jpg", // url
      // scaledSize: new google.maps.Size(100, 100), // scaled size
      // origin: new google.maps.Point(50, 50), // origin
      // anchor: new google.maps.Point(50, 50) // anchor
      // };
        
        var marker = new google.maps.Marker({
                position: myLatLng,
                map: map,
                // icon: icon
        });
        markers.push(marker);
      }

});