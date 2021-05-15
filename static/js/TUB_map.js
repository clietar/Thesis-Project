function initMap() {
    var options  = {
        zoom:13.2,
        center: {lat: 44.850575159765846, lng:0.4756162492496557},
        styles: [{
"elementType": "geometry",
"stylers": [
  {
    "color": "#f5f5f5"
  }
]
},
{
"elementType": "labels.icon",
"stylers": [
  {
    "visibility": "off"
  }
]
},
{
"elementType": "labels.text.fill",
"stylers": [
  {
    "color": "#616161"
  }
]
},
{
"elementType": "labels.text.stroke",
"stylers": [
  {
    "color": "#f5f5f5"
  }
]
},
{
"featureType": "administrative",
"elementType": "geometry",
"stylers": [
  {
    "visibility": "off"
  }
]
},
{
"featureType": "administrative.land_parcel",
"elementType": "labels.text.fill",
"stylers": [
  {
    "color": "#bdbdbd"
  }
]
},
{
"featureType": "poi",
"stylers": [
  {
    "visibility": "off"
  }
]
},
{
"featureType": "poi",
"elementType": "geometry",
"stylers": [
  {
    "color": "#eeeeee"
  }
]
},
{
"featureType": "poi",
"elementType": "labels.text.fill",
"stylers": [
  {
    "color": "#757575"
  }
]
},
{
"featureType": "poi.park",
"elementType": "geometry",
"stylers": [
  {
    "color": "#e5e5e5"
  }
]
},
{
"featureType": "poi.park",
"elementType": "labels.text.fill",
"stylers": [
  {
    "color": "#9e9e9e"
  }
]
},
{
"featureType": "road",
"elementType": "geometry",
"stylers": [
  {
    "color": "#ffffff"
  }
]
},
{
"featureType": "road",
"elementType": "labels.icon",
"stylers": [
  {
    "visibility": "off"
  }
]
},
{
"featureType": "road.arterial",
"elementType": "labels.text.fill",
"stylers": [
  {
    "color": "#757575"
  }
]
},
{
"featureType": "road.highway",
"elementType": "geometry",
"stylers": [
  {
    "color": "#dadada"
  }
]
},
{
"featureType": "road.highway",
"elementType": "labels.text.fill",
"stylers": [
  {
    "color": "#616161"
  }
]
},
{
"featureType": "road.local",
"elementType": "labels.text.fill",
"stylers": [
  {
    "color": "#9e9e9e"
  }
]
},
{
"featureType": "transit",
"stylers": [
  {
    "visibility": "off"
  }
]
},
{
"featureType": "transit.line",
"elementType": "geometry",
"stylers": [
  {
    "color": "#c43d3d"
  }
]
},
{
"featureType": "transit.station",
"elementType": "geometry",
"stylers": [
  {
    "color": "#eeeeee"
  }
]
},
{
"featureType": "water",
"elementType": "geometry",
"stylers": [
  {
    "color": "#c9c9c9"
  }
]
},
{
"featureType": "water",
"elementType": "labels.text.fill",
"stylers": [
  {
    "color": "#9e9e9e"
  }
]
}]
    }
    var map = new google.maps.Map(document.getElementById('plan'), options);
    map.data.loadGeoJson(
"https://raw.githubusercontent.com/clietar/Thesis-Project/main/Data/GeoJSON/ma_map_test.geojson"
);

// customizing  color and size  of lines and dotes
map.data.setStyle(function(feature) {
  var color = feature.getProperty('color');
  var icon = {
    url : feature.getProperty('icon'),
    scaledSize : new google.maps.Size(18,18)};
return {
fillColor: color,
strokeColor : color,
icon: icon,
strokeWeight: 3
}
});

// show selection of the line when the user point at the string line
map.data.addListener('mouseover', function(event) {
  map.data.revertStyle();
  map.data.overrideStyle(event.feature, {strokeWeight: 4, strokeColor: 'gray'});
  });
  map.data.addListener('mouseout', function(event) {
  map.data.revertStyle();
  });

// display info window with more detailed information
var infowindow = new google.maps.InfoWindow({
  disableAutoPan: true,
  maxWidth: 150
});
map.data.addListener('mouseover', function(event) {
  createInfoWindow(map, event, infowindow);
});

function createInfoWindow(map, event){
// Get properties from Data Layer to populate info window
  var name = event.feature.getProperty('name');
  var description = event.feature.getProperty('desc');
// Create content for info window
var contentString = '<div style="font-size:10px">'+
'<strong>' + name + '</strong>'+ '<p> </p>'+
'<p>' + description + '</p>'+'</div>'


// Create and open info window
infowindow.setContent(contentString);
infowindow.setPosition(event.latLng);
infowindow.open(map);
};
// close infowindwo when mouse does not hover it
map.data.addListener('mouseout', function() {
  setTimeout(function(){infowindow.close();}, '4000');
})



}