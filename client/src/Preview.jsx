import React from 'react'

export default function Preview({ videoUrl }) {

  function downloadAnimation() {
    const link = document.createElement('a');
    link.href = videoUrl;
    link.setAttribute('download', 'animation.mp4');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  return (
    <span className='preview-and-button'>
      <video className='preview' width="480" height="360" controls>
        <source src={videoUrl} type='video/mp4' />
        Your browser does not support the video tag.
      </video>

      <button className='download-btn' onClick={downloadAnimation}>Download</button>
    </span>
  )
}
