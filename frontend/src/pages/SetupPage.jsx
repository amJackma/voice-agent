import React, {useState} from 'react'
import {useNavigate} from 'react-router-dom'

const options = [
  'Mock Interview',
  'Resume Understanding Session',
  'Job Description Understanding Session',
  'Project Explanation'
]

export default function SetupPage(){
  const [name,setName] = useState('')
  const [designation,setDesignation] = useState('')
  const [resume,setResume] = useState(null)
  const [jd,setJd] = useState(null)
  const [mode,setMode] = useState(options[0])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const canStart = name && designation && resume

  async function start(e){
    e.preventDefault()
    setError('')
    setLoading(true)
    const fd = new FormData()
    fd.append('name', name)
    fd.append('designation', designation)
    fd.append('mode', mode)
    fd.append('resume', resume)
    if(jd) fd.append('jd', jd)

    try {
      const r = await fetch('http://127.0.0.1:8000/start-session', { method: 'POST', body: fd })
      if (!r.ok) {
        throw new Error(`Backend error: ${r.status} ${r.statusText}`)
      }
      const j = await r.json()
      console.log('Response:', j)
      if(j.session_id){
        navigate(`/interview/${j.session_id}`)
      } else {
        setError('No session_id in response: ' + JSON.stringify(j))
      }
    } catch(err) {
      console.error('Error:', err)
      setError(`Error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{padding:20}}>
      <h2>Setup</h2>
      <form onSubmit={start}>
        <div>
          <label>Name</label><br/>
          <input value={name} onChange={e=>setName(e.target.value)} />
        </div>
        <div>
          <label>Designation</label><br/>
          <input value={designation} onChange={e=>setDesignation(e.target.value)} />
        </div>
        <div>
          <label>Resume (PDF)</label><br/>
          <input type='file' accept='application/pdf' onChange={e=>setResume(e.target.files[0])} />
        </div>
        <div>
          <label>Job Description (optional)</label><br/>
          <input type='file' accept='application/pdf' onChange={e=>setJd(e.target.files[0])} />
        </div>
        <div>
          <label>Mode</label><br/>
          <select value={mode} onChange={e=>setMode(e.target.value)}>
            {options.map(o=> <option key={o}>{o}</option>)}
          </select>
        </div>
        <div style={{marginTop:12}}>
          <button type='submit' disabled={!canStart || loading}>Start Voice Session</button>
          {error && <div style={{color:'red',marginTop:8}}>{error}</div>}
          {loading && <div style={{color:'blue',marginTop:8}}>Loading...</div>}
        </div>
      </form>
    </div>
  )
}
