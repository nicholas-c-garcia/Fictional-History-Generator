import React, { useState, useEffect } from 'react';
import Overlay from "./Overlay";
import Empty from "./Empty";
import Obituary from './Obituary';

function Layout() {
  const [show, setShow] = useState(false);
  const [obituaries, setObituaries] = useState([]);

  const stupidID = '1';

  const setShowFunction = () => {
    setShow(!show)
  }

  useEffect(() => {
    getObituaries();
  }, []);

  const getObituaries = async () => {
    const res = await fetch (
      `https://uks6mtalpouwon36ggoctawavm0uqhod.lambda-url.ca-central-1.on.aws?stupidID=${stupidID}`,
      {
        method: "GET",
      }
    );

    if(res.status === 200){
      const backendData = await res.json()
      setObituaries(backendData["data"])
      console.log(backendData["data"])
    }
  }

  return (
    <div id="page">
      {!show ? (<></>) : (<div><Overlay setShowFunction={setShowFunction} obituaries={obituaries} setObituaries={setObituaries}/></div>)  }
      <header className="header" >
        <div className="addObituary">+ New Obituary</div>
        <h1 id="header-title">The Last Show</h1>
        <audio src={"/src/temp.mp3"}></audio>
        <button className="addObituary" onClick={() => setShow(!show)}>+ New Obituary</button>
      </header>
      <section>
        {obituaries.length === 0 ? 
          (<Empty/>) : 
          (
            <div id="obituaries">
              {obituaries.map((obituary) => {
                return (
                  <Obituary key={obituary.id} obituary={obituary} index={obituary.id}></Obituary>
                )
              })}
            </div>
          )}
      </section>
    </div>
    );
}

export default Layout;