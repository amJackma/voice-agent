import React, { useEffect, useState, useRef } from 'react'
import { useParams } from 'react-router-dom'
import '../styles/Interview.css'

export default function InterviewPage() {
  const { id } = useParams()
  const [session, setSession] = useState(null)
  const [agentMessages, setAgentMessages] = useState([])
  const [transcript, setTranscript] = useState('')
  const [userSpeech, setUserSpeech] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [error, setError] = useState('')
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const [running, setRunning] = useState(false)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/session/${id}`)
      .then(r => {
        if (!r.ok) throw new Error(`Session fetch failed: ${r.status}`)
        return r.json()
      })
      .then(data => {
        setSession(data)
        // Play welcome message only AFTER session data is loaded
        const welcomeMsg = "Welcome to JHEX, for your interview preparation. Let's begin."
        setAgentMessages([welcomeMsg])
        speak(welcomeMsg)
      })
      .catch(err => {
        console.error('Session load error:', err)
        setError(`Failed to load session: ${err.message}`)
      })
  }, [id])

  function speak(text) {
    setIsSpeaking(true)
    const ut = new SpeechSynthesisUtterance(text)
    ut.onend = () => setIsSpeaking(false)
    ut.onerror = () => setIsSpeaking(false)
    window.speechSynthesis.speak(ut)
  }

  async function startMic() {
    if (!navigator.mediaDevices) {
      setError('Microphone not available in this browser.')
      return
    }
    setError('')
    setIsListening(true)

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      // Use the browser's preferred MIME type instead of forcing audio/wav
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : ''  // let browser choose default

      const options = mimeType ? { mimeType } : {}
      const mr = new MediaRecorder(stream, options)
      mediaRecorderRef.current = mr
      chunksRef.current = []

      mr.ondataavailable = e => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mr.onstop = async () => {
        setIsListening(false)
        setProcessing(true)
        setError('')

        // Stop all tracks to release the mic
        stream.getTracks().forEach(t => t.stop())

        // Use the actual recorded MIME type
        const actualType = mr.mimeType || 'audio/webm'
        const ext = actualType.includes('webm') ? 'webm' : actualType.includes('ogg') ? 'ogg' : 'wav'
        const blob = new Blob(chunksRef.current, { type: actualType })

        try {
          // Send to STT
          const fd = new FormData()
          fd.append('audio', blob, `speech.${ext}`)
          const r = await fetch('http://127.0.0.1:8000/stt', { method: 'POST', body: fd })
          if (!r.ok) throw new Error(`STT failed: ${r.status} ${r.statusText}`)
          const j = await r.json()
          const text = j.text || ''
          setUserSpeech(text)
          setTranscript(prev => prev + (prev ? '\n' : '') + 'You: ' + text)

          // Send to /ask to get next question
          const askFd = new FormData()
          askFd.append('session_id', id)
          askFd.append('user_text', text)
          const rq = await fetch('http://127.0.0.1:8000/ask', { method: 'POST', body: askFd })
          if (!rq.ok) throw new Error(`Ask failed: ${rq.status} ${rq.statusText}`)
          const aj = await rq.json()
          if (aj.agent) {
            setAgentMessages(prev => [...prev, aj.agent])
            setTranscript(prev => prev + '\nAgent: ' + aj.agent)
            speak(aj.agent)
          }
        } catch (err) {
          console.error('Interview error:', err)
          setError(`Error: ${err.message}`)
        } finally {
          setProcessing(false)
        }
      }

      mr.start()
      setRunning(true)
    } catch (err) {
      console.error('Mic error:', err)
      setIsListening(false)
      setError(`Microphone error: ${err.message}`)
    }
  }

  function stopMic() {
    const mr = mediaRecorderRef.current
    if (mr && mr.state !== 'inactive') mr.stop()
    setRunning(false)
  }

  async function endInterview() {
    setProcessing(true)
    setError('')
    try {
      const fd = new FormData()
      fd.append('session_id', id)
      const r = await fetch('http://127.0.0.1:8000/score', { method: 'POST', body: fd })
      if (!r.ok) throw new Error(`Score failed: ${r.status} ${r.statusText}`)
      const j = await r.json()
      const result = j.result || {}

      // Build a readable result string
      let resultText = ''
      if (result.score !== undefined) {
        resultText += `Score: ${result.score}/100\n\n`
      }
      if (result.strengths) {
        resultText += 'Strengths:\n'
        const strengths = Array.isArray(result.strengths) ? result.strengths : [result.strengths]
        strengths.forEach(s => { resultText += `  • ${s}\n` })
        resultText += '\n'
      }
      if (result.weaknesses) {
        resultText += 'Weak Areas:\n'
        const weaknesses = Array.isArray(result.weaknesses) ? result.weaknesses : [result.weaknesses]
        weaknesses.forEach(w => { resultText += `  • ${w}\n` })
        resultText += '\n'
      }
      if (result.recommendation) {
        resultText += `Hiring Recommendation: ${result.recommendation}\n`
      }
      if (!resultText) {
        resultText = JSON.stringify(result, null, 2)
      }

      setAgentMessages(prev => [...prev, 'Interview finished. See results below.', resultText])
      speak('Interview finished. Showing results.')
    } catch (err) {
      console.error('Score error:', err)
      setError(`Scoring error: ${err.message}`)
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className="interview-container">
      <div className="interview-header">
        <h1>🎤 JHEX Interview</h1>
        {session && (
          <div className="candidate-info">
            <strong>{session.name}</strong> • {session.designation}
            {isSpeaking && <span className="status-badge status-speaking" style={{ marginLeft: 15 }}>🔊 Speaking</span>}
            {isListening && <span className="status-badge status-listening" style={{ marginLeft: 15 }}>🎙️ Listening</span>}
            {processing && <span className="status-badge status-listening" style={{ marginLeft: 15 }}>⏳ Processing</span>}
            {!isSpeaking && !isListening && !processing && <span className="status-badge status-idle" style={{ marginLeft: 15 }}>⏸ Idle</span>}
          </div>
        )}
      </div>

      {error && (
        <div style={{ maxWidth: 900, margin: '0 auto 15px', padding: '12px 20px', background: '#fff3f3', border: '1px solid #ffcdd2', borderRadius: 12, color: '#c62828', fontWeight: 600 }}>
          ⚠️ {error}
        </div>
      )}

      <div className="interview-main">
        {/* Agent Section */}
        <div className="agent-section">
          <div className="agent-header">Interview Agent</div>

          {isSpeaking && (
            <div className="speaking-indicator">
              <div className="speaking-bar"></div>
              <div className="speaking-bar"></div>
              <div className="speaking-bar"></div>
              <div className="speaking-bar"></div>
              <div className="speaking-bar"></div>
            </div>
          )}

          <div className="agent-messages">
            {agentMessages.map((m, i) => (
              <div key={i} className="agent-message" style={m.includes('Score:') ? { fontFamily: 'monospace', whiteSpace: 'pre-wrap', fontSize: 13 } : {}}>{m}</div>
            ))}
          </div>

          {isListening && (
            <div className="listening-indicator">
              <div className="listening-dot"></div>
              <div className="listening-dot"></div>
              <div className="listening-dot"></div>
              <span style={{ marginLeft: 10, color: '#667eea', fontWeight: 600, fontSize: 12 }}>LISTENING...</span>
            </div>
          )}
        </div>

        {/* User Transcript Section */}
        <div className="user-section">
          <div className="user-header">Your Transcript</div>
          <div className="user-transcript">{transcript}</div>
        </div>

        {/* Controls */}
        <div style={{ gridColumn: '1 / -1' }}>
          <div className="controls">
            <button className="btn btn-primary" onClick={startMic} disabled={running || processing}>
              🎤 Start Mic
            </button>
            <button className="btn btn-primary" onClick={stopMic} disabled={!running}>
              ⏹ Stop Mic
            </button>
            <button className="btn btn-danger" onClick={endInterview} disabled={processing} style={{ marginLeft: 12 }}>
              ✓ End Interview (Score)
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
