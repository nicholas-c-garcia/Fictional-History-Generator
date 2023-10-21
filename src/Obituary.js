import React, { useState } from 'react';
import useSound from 'use-sound';

function Obituary({ obituary, index }) {

//Put showObit into layout, pass to both Obituary.js and Layout.js to set newly created obituary to be open

  const [button, setButton] = useState("▶️")
  const [showObit, setShowObit] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [play, { pause }] = useSound (
    obituary.audio,
    {volume: 1.0}
  );

  const options = {
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  
  const formatDate = (when) => {
    const formatted = new Date(when).toLocaleString("en-US", options);
    if (formatted === "Invalid Date") {
      return "";
    }
  
    return formatted;
  };

  const showObituary = () => {
    setShowObit(!showObit)
  }

  const playSound = () => {
    if(!isPlaying) {
      setIsPlaying(true);
      play();
      setButton("⏸︎")
    }
    else {
      setIsPlaying(false);
      pause(); 
      setButton("▶️");
    }
  }

  return (
      <div id="obit-Card" key={`obit-card-${index}`}>
        <img id="obit-pic" onClick={showObituary} src={obituary.img} style={{ width: 'inherit', alignSelf: 'center' }}></img>
        <p id="obit-text-element" onClick={showObituary}>{obituary.name}</p>
        <p id="obit-text-element" onClick={showObituary}>{formatDate(obituary.year_born)} - {formatDate(obituary.year_died)}</p>
        {!showObit ? 
          (<p></p>) :
          (<div id="pull-down"> 
              <p id="obit-text-element" onClick={showObituary}>{obituary.output}</p>
              <button id="voice-button" onClick={playSound}>{button}</button>
            </div>)
        }
      </div>
  )
}
  
export default Obituary;
  
