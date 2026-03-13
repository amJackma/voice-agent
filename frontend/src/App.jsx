import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import SetupPage from './pages/SetupPage'
import InterviewPage from './pages/InterviewPage'

export default function App(){
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<SetupPage/>} />
        <Route path='/interview/:id' element={<InterviewPage/>} />
      </Routes>
    </BrowserRouter>
  )
}
