import L from "leaflet";

function Icon(bus) {

  const arrows = { "WestBound": "&larr;", "EastBound": "&rarr;", "SouthBound": "&darr;", "NorthBound": "&uarr;" }

  const classname = ["WestBound", "EastBound"].includes(bus.dir) ? "block": "";
  if (bus.route.toLowerCase().indexOf("owl") > -1) {
    bus.route = "<small>OWL</small>";
  }

  return (
    L.divIcon({
      html: `<div class='icon'>${bus.route}&nbsp;<span class='${classname}'>${arrows[bus.dir]}</span></div>`,
      iconSize: [0, 0],
      iconAnchor: [35, 13]
    })
  );
}

export default Icon;
