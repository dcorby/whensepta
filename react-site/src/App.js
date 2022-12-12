import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import { MapContainer } from "react-leaflet/MapContainer";
import { TileLayer } from "react-leaflet/TileLayer";
import { LayerGroup } from "react-leaflet/LayerGroup";
import { Marker } from "react-leaflet/Marker";
import Icon from "./Icon";
import Clock from "./Clock";

function App() {
  const [buses, setBuses] = useState([]);
  const [seconds, setSeconds] = useState(0);
  const initRef = useRef(false);
  const layerGroupRef = useRef();

  window["callback"] = function(json) {
    const buses = [];
    for (const route in json.routes[0]) {
      json.routes[0][route].forEach((bus) => {
        const dict = { "lat": bus.lat, "lng": bus.lng, "route": route, "dir": bus.Direction };
        dict.icon = Icon(dict);
        buses.push(dict);
      });
    }
    //layerGroupRef.current.clearLayers();  react will manage this
    setBuses(buses);
    setSeconds(0);
    document.querySelector("script#jsonp").remove();
  }

  function refresh(e) {
    const url = "https://www3.septa.org/hackathon/TransitViewAll/?callback=callback&s=" + (new Date()).getTime();
    const script = document.createElement("script");
    script.id = "jsonp";
    script.src = url;
    document.body.appendChild(script);
  }

  useEffect(() => {
    // to prevent this getting called twice in strict mode
    if (initRef.current) { return; }
    initRef.current = true;
    refresh(); 
  }, []);

  return (
    <MapContainer id="map" center={[39.9526, -75.1652]} zoom={13}>
    <TileLayer
      attribution="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> and <a href='https://www.thunderforest.com/'>Thunderforest</a>"
      url="https://tile.thunderforest.com/transport/{z}/{x}/{y}.png?apikey=44691b3e3bf7441086137f894ae46dda"
    />
    <LayerGroup ref={layerGroupRef}>
      {
        buses.map((bus, idx) => 
          <Marker key={`bus-${idx}`} position={[bus.lat, bus.lng]} icon={bus.icon} />
        )
      }
    </LayerGroup>
    <Clock refresh={refresh} seconds={seconds} setSeconds={setSeconds} />
    </MapContainer>
  );
}

export default App;
