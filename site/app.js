"use strict";

var map = L.map("map").setView([39.9526, -75.1652], 15);
var tiles = "http://localhost:3001/tiles/drawn/{z}/{x}/{y}.png";
if (location.hostname === "www.whensepta.com") {
  tiles = "https://tile.thunderforest.com/transport/{z}/{x}/{y}.png?apikey=44691b3e3bf7441086137f894ae46dda";
}
var tile_layer = L.tileLayer(tiles, {
  minZoom: 12,
  maxZoom: 18,
  attribution: "&copy; <a href='http://www.openstreetmap.org/copyright'>OpenStreetMap</a>"
});
tile_layer.addTo(map);
if (false) {
  // choose not to annoy
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function (position) {
      return map.panTo([position.coords.latitude, position.coords.longitude]);
    }, function (err) {
      return console.warn("Geolocation error (".concat(err.code, "): ").concat(err.message));
    }, {
      timeout: 3000
    });
  }
}
var active = document.querySelector("div#active");
var markers = L.layerGroup().addTo(map);
var state = {
  markers: markers,
  seconds: 0,
  active: null
};
var arrows = {
  "WestBound": "&larr;",
  "EastBound": "&rarr;",
  "SouthBound": "&darr;",
  "NorthBound": "&uarr;"
};
function get_icon(route, direction) {
  var classname = ["WestBound", "EastBound"].includes(direction) ? "block" : "";
  if (route.toLowerCase().indexOf("owl") > -1) {
    route = "<small>OWL</small>";
  }
  var icon = L.divIcon({
    html: "<div class='icon'>".concat(route, "&nbsp;<span class='").concat(classname, "'>").concat(arrows[direction], "</span></div>"),
    iconSize: [0, 0],
    iconAnchor: [35, 13]
  });
  return icon;
}
function callback(json) {
  var buses = [];
  var _loop = function _loop(route) {
    json.routes[0][route].forEach(function (bus) {
      var marker = L.marker([bus.lat, bus.lng], {
        icon: get_icon(route, bus.Direction)
      });
      buses.push(marker);
    });
  };
  for (var route in json.routes[0]) {
    _loop(route);
  }
  state.markers.clearLayers();
  buses.forEach(function (marker) {
    marker.addTo(state.markers);
  });
  if (buses.length > 0) {
    state.seconds = 0;
  }
}
function refresh_buses() {
  var url = "https://www3.septa.org/hackathon/TransitViewAll/?callback=callback";
  var script = document.createElement("script");
  script.src = url;
  document.body.appendChild(script);
}
var timer = document.querySelector("div#timer");
setInterval(function () {
  state.seconds++;
  var label = "".concat(Math.floor(state.seconds / 60), "m ").concat(state.seconds % 60, "s");
  timer.innerText = label;
}, 1000);
var reload = document.querySelector("div#reload");
reload.addEventListener("click", function () {
  refresh_buses();
});
refresh_buses();
