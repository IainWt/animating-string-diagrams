import React from 'react'


export default function ExampleTikz() {
  return (
    <div className='example-tikz'>
      <h2 className='example-title'>Example</h2>
      <p>
        If you do not have diagrams ready, try copying the TikZ below:
      </p>
      <p className='tikz-title'>Styles:</p>
      <div className='example-tikz-code'>
        {`\\tikzstyle{red dot}=[fill=red, draw=black, shape=circle]`} <br />
        {`\\tikzstyle{green dot}=[fill=green, draw=black, shape=circle]`}
      </div>
      <p className='tikz-title'>TikZ Diagram 1:</p>
      <div className='example-tikz-code'>
        {`\\node [style=none] (0) at (-5, 0) {};`} <br />
        {`\\node [style=red dot] (1) at (-2, 0) {$a$};`}<br />
        {`\\node [style=green dot] (2) at (2, -2) {$b$};`} <br />
        {`\\node [style=red dot] (3) at (3, 2) {$c$};`} <br />
        {`\\node [style=none] (4) at (5, 0) {};`} <br />
        {`\\draw (0) to (1);`} <br />
        {`\\draw [bend right=60, looseness=1.25] (1) to (2);`} <br />
        {`\\draw [in=-180, out=20, looseness=1.5] (1) to (3);`} <br />
        {`\\draw [in=-180, out=0, looseness=1.5] (2) to (4);`} <br />
      </div>
      <p className='tikz-title'>TikZ Diagram 2:</p>
      <div className='example-tikz-code'>
        {`\\node [style=none] (0) at (-5, 0) {};`} <br />
        {`\\node [style=red dot] (1) at (-2, 0) {$a$};`}<br />
        {`\\node [style=green dot] (2) at (0, -2) {$b$};`} <br />
        {`\\node [style=red dot] (3) at (3, 2) {$c$};`} <br />
        {`\\node [style=none] (4) at (5, 0) {};`} <br />
        {`\\draw (0) to (1);`} <br />
        {`\\draw [in=160, out=-45, looseness=1.25] (1) to (4);`} <br />
        {`\\draw [in=-180, out=20, looseness=1.5] (1) to (3);`} <br />
        {`\\draw [in=-180, out=0, looseness=1.5] (2) to (4);`} <br />
      </div>
    </div>
  )
}
