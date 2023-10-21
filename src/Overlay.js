import { v4 as uuidv4 } from "uuid";
import React, { useState } from 'react';

function Overlay({ setShowFunction, obituaries, setObituaries }) {

  var imageFile

  const setShowFunction2 = () => {
      setShowFunction();
  };

  const setImage = (file) => {
    imageFile = file;
    console.log(imageFile) 
  }

  // Gives inputted info to DynamoDB
  const addObituary = async () => {

    setShowFunction2();

    const name = document.getElementById("overlay-text").value
    const img = document.getElementById("overlay-upload").files[0].name; 
    const dateBorn = document.getElementById("overlay-date1").value
    const dateDied = document.getElementById("overlay-date2").value

    const formData = new FormData();
    formData.append('stupidID', '1');
    formData.append('id', uuidv4());
    formData.append('name', name);
    formData.append('img_path', img);
    formData.append('born_year', dateBorn);
    formData.append('died_year', dateDied);
    formData.append('image_file', imageFile);

    const res = await fetch(
        "https://in2s5nttosntgkzpm2bvd7y5nm0phovc.lambda-url.ca-central-1.on.aws/",
        {
          method : "POST",
          body : formData
        }
      )
      if(res.status === 200){
        const backendData = await res.json()
        setObituaries(obituaries => [...obituaries, backendData["data"]])
        console.log(backendData["data"])
      }
 
      console.log("ADD OBITUARY CALLED TO COMPLETION")
    }

    const handleImageChange = (event) => {
      const file = event.target.files[0];
      setImage(file);
      //console.log(file); This works
    }

    return (
        <div id='create-obituary'>
          <button className='exit-overlay' onClick={setShowFunction2}>X</button>
          <div id="overlay">
            <h1>Create a New Obituary</h1>
            <img src="https://pbs.twimg.com/tweet_video_thumb/C0HpLYlXEAANFnK.jpg" id="overlay-image" alt="beautiful"></img>
            <label for="overlay-upload" id="overlay-upload-text">Select an Image for the Deceased</label>
            <input type="file" accept="image/png" id="overlay-upload" onChange={handleImageChange}></input>
            <input type="text" placeholder="Name of Deceased" id="overlay-text"></input>
            <div>When that dude die?</div>
            <div id="overlay-date-flex">
                <input type="datetime-local" id="overlay-date1" name="born"></input>
                <input type="datetime-local" id="overlay-date2" name="died"></input>
            </div>
            <button onClick={addObituary}>WRITE OBITUARY</button>
          </div>
        </div>
    )
}

export default Overlay;