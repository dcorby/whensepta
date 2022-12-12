let map = L.map("map").setView([39.9526, -75.1652], 15);

let tiles = "http://localhost:3001/tiles/drawn/{z}/{x}/{y}.png";
if (location.hostname === "www.whensepta.com") {
  tiles = "https://tile.thunderforest.com/transport/{z}/{x}/{y}.png?apikey=44691b3e3bf7441086137f894ae46dda";
}

const tile_layer = L.tileLayer(tiles, {
    minZoom: 12,
    maxZoom: 18,
    attribution: "&copy; <a href='http://www.openstreetmap.org/copyright'>OpenStreetMap</a>"
})

tile_layer.addTo(map);

if (false) {
  // choose not to annoy
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => map.panTo([position.coords.latitude, position.coords.longitude]),
      (err) => console.warn(`Geolocation error (${err.code}): ${err.message}`),
      { timeout: 3000 }
    );
  }
}

const active = document.querySelector("div#active");
const markers = L.layerGroup().addTo(map);
const state = { markers: markers, seconds: 0, active: null }
const arrows = { "WestBound": "&larr;", "EastBound": "&rarr;", "SouthBound": "&darr;", "NorthBound": "&uarr;" }

function get_icon(route, direction) {
  const classname = ["WestBound", "EastBound"].includes(direction) ? "block": "";
  if (route.toLowerCase().indexOf("owl") > -1) {
    route = "<small>OWL</small>";
  }
  const icon = L.divIcon({
    html: `<div class='icon'>${route}&nbsp;<span class='${classname}'>${arrows[direction]}</span></div>`,
    iconSize: [0, 0],
    iconAnchor: [35, 13]
  });
  return icon;
}

function callback(json) {
  const buses = [];
  for (const route in json.routes[0]) {
    json.routes[0][route].forEach((bus) => {
      const marker = L.marker([bus.lat, bus.lng], { icon: get_icon(route, bus.Direction) });
      buses.push(marker);
    });
  }

  state.markers.clearLayers();
  buses.forEach((marker) => {
    marker.addTo(state.markers);
  });
  if (buses.length > 0) {
    state.seconds = 0;
  }
}

function refresh_buses() {
  const url = "https://www3.septa.org/hackathon/TransitViewAll/?callback=callback"
  const script = document.createElement("script");
  script.src = url;
  document.body.appendChild(script);
}

const timer = document.querySelector("div#timer");
setInterval(() => {
  state.seconds++;
  const label = `${Math.floor(state.seconds / 60)}m ${state.seconds % 60}s`;
  timer.innerText = label;
}, 1000);

const reload = document.querySelector("div#reload");
reload.addEventListener("click", () => {
  refresh_buses(); 
});
refresh_buses();

