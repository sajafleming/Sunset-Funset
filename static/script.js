"use strict";
$(document).ready(function () {

  var mapProp = {
    center: new google.maps.LatLng(37.7749,-122.4194),
    zoom:10,
    mapTypeId:google.maps.MapTypeId.TERRAIN
  };

  // new google maps objects
  var map = new google.maps.Map($("#googleMap")[0], mapProp);
  var markers = [];
  var infoWindows = [];
  var userLat;
  var userLng;
  var directionsService;
  var directionsDisplay;
  // new google maps geocoder object
  var geocoder = new google.maps.Geocoder();

  // for showing directions
  directionsService = new google.maps.DirectionsService();
  directionsDisplay = new google.maps.DirectionsRenderer();
  directionsDisplay.setMap(map);
  directionsDisplay.setOptions( { suppressMarkers: true } );

  // if geolocation can obtain location from browser, center map on user location
  if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function (position) {
      var initialLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
      map.setCenter(initialLocation);
    });
  }
         
  // disables the button and turns text to "loading..."
  $('#submit-location').on('click', function () {
    var $this = $(this);
    $this.button('loading');
  });
         
  // getting values from user text box
  $('#user-input-form').submit(function(evt) {
    evt.preventDefault()
  
    geocodeAddress(geocoder, map);
  });

  // i don't think this does anything
  $('#user-textbox').submit(function(evt) {
    //geocodeAddress(geocoder, map);
  });

  // Get the HTML input element for the autocomplete search box
  var input = $('#user-textbox')[0]

  // Create the autocomplete object
  var autocomplete = new google.maps.places.Autocomplete(input);

  // Clears textbox when user starts typing
  $('input:text').focus(function(evt) {
    $(this).val('');
  });

  // Get the <span> element that closes the modal
  var span = document.getElementsByClassName("close")[0];
  // When the user clicks on <span> (x), close the modal
  span.onclick = function() {
    $('#error-modal').css('display', 'none');
  }

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

  // convert address to latlong to send to backend
  function geocodeAddress(geocoder, resultsMap) {
    var address = $('#user-textbox').val()
    geocoder.geocode({'address': address}, function(results, status) {
      console.log(results)
      if (status === google.maps.GeocoderStatus.OK) {
        // Clear out old markers
        while (markers.length > 0) {
          markers.pop().setMap(null);
          // mainMarker.pop().setMap(null);
        }

        resultsMap.setCenter(results[0].geometry.location);

        // get the latlong from the user's entered location
        console.log("Lat " + results[0].geometry.location.lat());
        console.log("Lng " + results[0].geometry.location.lng());

        var lat = results[0].geometry.location.lat();
        var lng = results[0].geometry.location.lng();
        userLat = lat;
        userLng = lng;

        // get the lat and long that the user entered and the radius
        var params = {"lat": lat, "lng": lng, 
          "radio": $('input[name=radius]:checked').val()};

        // ajax to get sunset latlongs and pictures
        $.get("/sunset-spots", params, plotSunsetSpots);

        // plot the original point
        var enteredLocation = new google.maps.Marker({
          map: resultsMap,
          icon: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png",
          position: results[0].geometry.location,
          animation: google.maps.Animation.DROP
        });

        google.maps.event.addListener(enteredLocation, 'click', function() {
          //$('#myModal').modal('show');
        });

        markers.push(enteredLocation)

      } else {
        alert('Geocode was not successful for the following reason: ' + status);
      }
    });
  }

  // function to plot sunsets points
  function plotSunsetSpots(data) {
    if (data.hasOwnProperty("error")) {
      // show error message
      $('#error-modal').css('display', 'block');
    } else {

      // data from ajax call
      var sunsetCoordinates = data.sunset_spots;
      var coordinatesLength = sunsetCoordinates.length;

      // add pins
      for (var i = 0; i < coordinatesLength; i++) {
        console.log(sunsetCoordinates[i].lat, sunsetCoordinates[i].lng);
        console.log(sunsetCoordinates[i].urls, sunsetCoordinates[i].elv);

        var myLatLng = {lat: sunsetCoordinates[i].lat, lng: sunsetCoordinates[i].lng};
        var urls = sunsetCoordinates[i].urls;
        var elevation = sunsetCoordinates[i].elv

        // get address from geocoder
        // var address = geocodeLatLng(myLatLng, geocoder, map);

        geocoder.geocode({'location': myLatLng}, makeGeocodeCallback(myLatLng, urls, elevation));
      }

    // stop loading button here (once points are plotted)
      $('#submit-location').button('reset');
    }
  }

  function makeGeocodeCallback(latLng, urls, elevation) {
    return function(results, status) {
          var addressName = '';
          var address = '';

          if (status === 'OK') {
            if (results[0]) {
              addressName = results[1].formatted_address
              address = results[0].formatted_address
            } else {
              console.log('No results found');
            }
          } else {
            console.log('Geocoder failed due to: ' + status);
          }

          console.log(addressName);
          console.log(address);
          
          var contentString = '<div id="content">'+
              '<div id="siteNotice">'+
              '</div>'+
              '<h5 id="firstHeading" class="firstHeading">'+
              addressName +
              '</h5>'+
              '<h6 id="secondHeading" class="secondHeading">'+
              address +
              '</h6>'+
              '<div id="bodyContent">'+
              elevation + ' feet'+
              '</div>'+
              '<div>'+
              '<a id="see-pictures">see pictures</a>'
              '</div>'+
              '</div>';

          console.log("the urls: ");
          console.log(urls);

          markers.push(addMarker(latLng, urls, contentString));

        };
  }

  // add markers to the map
  function addMarker(myLatLng, urls, content) {
    
    var image = "http://maps.google.com/mapfiles/ms/icons/red-dot.png"; // smaller pin
    var marker = new google.maps.Marker({
      position: myLatLng,
      map: map,
      animation: google.maps.Animation.DROP
      // icon: image
    });

    // create new info window object
    var infowindow = new google.maps.InfoWindow({
      content: content
    });

    marker.addListener('click', function() {
          while (infoWindows.length > 0) {
            infoWindows.pop().setMap(null);
          }
          infowindow.open(map, marker);
          infoWindows.push(infowindow);

          // call get directions here
          getDirections(myLatLng);

          // After you open the info window, the see-pictures element exists, so
          // we can now define its click handler.
          $("#see-pictures").click(function(evt) {
            showPictures(myLatLng, urls);
          });
        });

    // // listener for when marker clicked, success function is showpics
    // marker.addListener('click', function(evt) { 
    //   showPictures(myLatLng, urls);
    //   // loop through and set each icon back to default, except for the first one (the point searched for)
    //   for (var i = 1; i < markers.length; i++) {
    //     markers[i].setIcon(null);
    //   }
    //   // change the selected marker to the sunpin 
    //   this.setIcon("http://i66.tinypic.com/17wjro.png");
    // });

    return marker;
  }

  // turn the final latlongs into the names of human readable locations!
  function geocodeLatLng(latlng) {

    geocoder.geocode({'location': latlng}, function(results, status) {
      var address = '';

      if (status === 'OK') {
        if (results[0]) {
          console.log(results[0].formatted_address)
          address = results[0].formatted_address
        } else {
          console.log('No results found');
        }
      } else {
        console.log('Geocoder failed due to: ' + status);
      }

      console.log(address)

        var contentString = '<div id="content">'+
            '<div id="siteNotice">'+
            '</div>'+
            '<h1 id="firstHeading" class="firstHeading">' +
            address +
            '</h1>'+
            '<div id="bodyContent">'+
            '</div>'+
            '</div>';

        markers.push(addMarker(latlng, sunsetCoordinates[i].urls, contentString));
    });

  };

  // function for getting directions
  function getDirections(myLatLng) {
    var destinationLat = myLatLng['lat'];
    var destinationLng = myLatLng['lng'];
    
    var request = {
        origin: {lng: userLng, lat: userLat},
        destination: {lng: Number(destinationLng), lat: Number(destinationLat)},
        travelMode: google.maps.TravelMode["DRIVING"]
    };
    directionsService.route(request, function(response, status) {
      if (status == google.maps.DirectionsStatus.OK) {
        directionsDisplay.setDirections(response);
      }
    });
  }

  // new and improved modal to show pics <3
  function showPictures(latlong, urls) {
    $('.carousel-inner').empty();

    // add pictures for pin selected
    var picturesLength = urls.length;

    if (urls.length === 0) {
      $("#no-pics").modal()
    } else { 

      $("#modal-pics").modal()

      // urls = [photo_url, photo_source_url]
      console.log(urls);
      for (var i = 0; i < picturesLength; i++) {
        console.log(urls[i])

        var pic = urls[i][0]
        var link = urls[i][1]
        var html = '<div class="item';

        console.log(pic);

        console.log(link);

        if (i === 0) {
          html += ' active';
        }

        html += '"><a href="';
        html += link + '" target="_blank"><img class="img-responsive" src="';
        html += pic + '" class="my-img"></img></a></div>';
        $('.carousel-inner').append(html);
      }
    }

    // bootstrap carousel - supposed to not move on it's own, but it is anyway
    $('.carousel').carousel({
      interval: false
    });

  }




});