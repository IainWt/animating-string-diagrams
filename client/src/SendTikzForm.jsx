// @flow

import React, { useState, useEffect } from 'react'
import Preview from './Preview'
import ErrorMessage from './ErrorMessage'
import ExampleTikz from './ExampleTikz'
import WelcomeMessage from './WelcomeMessage'

const BASE_URL = "http://127.0.0.1:8000/"
// const BASE_URL = "http://sd-backend-eb-env.eba-hyijwrxw.us-east-1.elasticbeanstalk.com/"
// const BASE_URL = "https://iainweetman.site/"

export default function SendTikzForm() {

  const [stylesInput, setStylesInput] = useState('')
  const [inputs, setInputs] = useState({0: { tikz: '', subtitle: '' }})
  const [videoUrl, setVideoUrl] = useState('')
  const [errorMessage, setErrorMessage] = useState(false)

  function addInput() {
    setInputs(prevInputs => {
      const newInputs = {...prevInputs}
      newInputs[(Object.keys(inputs)).length] = { tikz: '', subtitle: '' }
      return newInputs
    })
  }


  function handleInputTikzChange(id, value) {
    // Create new inputs array with updated value
    setInputs(prevInputs => {
      let newInputs = {...prevInputs}
      newInputs[id].tikz = value
      return newInputs
    })
  }

  function handleInputChange(id, value) {
    // Create new inputs array with updated value
    setInputs(prevInputs => {
      let newInputs = {...prevInputs}
      newInputs[id].subtitle = value
      return newInputs
    })
  }

  function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage(false)
    setVideoUrl('')

    fetch(BASE_URL + 'test/', {
      method: 'POST',
      body: JSON.stringify({stylesInput, 'diagrams': inputs}),
      headers: {'Content-type': 'application/json; charset=UTF-8'}
    })
    .then(response => {
      console.log(response.status)
      // return response.json()
      for (var pair of response.headers.entries()) {
        if (pair[0] === 'content-type' && !pair[1]) setErrorMessage(true)
      }
      return response.blob()
    })
    // .then(data => console.log(data))
    .then(videoBlob => {
      // Create a link and click it to download the video
      const url = window.URL.createObjectURL(new Blob([videoBlob]));
      setVideoUrl(url)
    })
    .catch(error => setErrorMessage(error))
  } 


  function clearInputs() {
    setStylesInput('')
    setInputs(prevInputs => {
      let newInputs = {...prevInputs}
      for (let id in Object.keys(newInputs)) {
        Object.keys(newInputs[id]).forEach(innerKey => {
          newInputs[id][innerKey] = ''
        })
      }
      return newInputs
    })
  }


  return (
    <>
      <h1>Animating String Diagrams</h1>
      <WelcomeMessage />
      {errorMessage && <ErrorMessage />}

      <div className='outer-element'>

        <ExampleTikz />

        <fieldset className='send-tikz-form'>
          <legend>Create Animation</legend>
          <button className='danger-btn' onClick={clearInputs}>Clear All</button>

          <label className='style-label' htmlFor='stylesText'>TikZ Styles</label>
          <textarea 
            id='stylesText'
            value={stylesInput}
            onChange={(e) => setStylesInput(e.target.value)}
          />

          {(Object.keys(inputs)).map(id => {
            return(
              <div key={id}>
                <label htmlFor={'tikz' + id}>TikZ Diagram</label>
                <textarea 
                  id={'tikz' + id}
                  value={inputs[id].tikz}
                  onChange={(e) => handleInputTikzChange(id, e.target.value)}
                />
                <label htmlFor={'subtitle' + id}>Subtitle</label>
                <input
                  id={'subtitle' + id}
                  value={inputs[id].subtitle}
                  onChange={(e) => handleInputChange(id, e.target.value)}
                />
              </div>
            )
          })}

          <button className='add-btn' onClick={addInput}>Add TikZ Diagram</button>
          <button className='submit-btn' onClick={handleSubmit}>Create animation</button>
        </fieldset>

        {videoUrl && !errorMessage && (
          <Preview videoUrl={videoUrl} />
        )}

      </div>
    </>
  )
}

 
