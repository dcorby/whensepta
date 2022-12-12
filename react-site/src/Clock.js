import React, { useRef, useEffect } from "react";
import "./Clock.css";

function Clock({ refresh, seconds, setSeconds }) {
  const initRef = useRef(false);

  useEffect(() => {
    // to prevent this getting called twice in strict mode
    if (initRef.current) { return; }
    initRef.current = true;
    setInterval(() => {
      setSeconds((prev) => prev + 1)
    }, 1000);
  });

  return (
  <div id="clock">
    <div id="reload">
      <span id="button" onClick={refresh}>Refresh</span>
    </div>
    <div id="timer">
      {`${Math.floor(seconds / 60)}m ${seconds % 60}s`}
    </div>
  </div>
  );
}

export default Clock;

