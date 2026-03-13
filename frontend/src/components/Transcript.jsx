import React from 'react'

export default function Transcript({text}){
  return <pre style={{whiteSpace:'pre-wrap',background:'#f7f7f7',padding:10}}>{text}</pre>
}
