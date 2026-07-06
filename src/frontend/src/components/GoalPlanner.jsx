import React, { useState } from 'react'

function GoalPlanner({ connected, config }) {
  const [formData, setFormData] = useState({ age: 30, risk: 5, horizon: 5 })
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await fetch('/api/goals/plan/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          age: formData.age,
          risk_appetite: formData.risk,
          time_horizon: formData.horizon
        })
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to generate plan')
      }
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <section>
      <h2>🎯 Goal Planner</h2>
      <form onSubmit={submit}>
        <label>Age: <input type="number" value={formData.age} onChange={e => setFormData({...formData, age: +e.target.value})} /></label>
        <label>Risk Appetite (1-10): <input type="range" min="1" max="10" value={formData.risk} onChange={e => setFormData({...formData, risk: +e.target.value})} /></label>
        <label>Time Horizon (years): <input type="number" value={formData.horizon} onChange={e => setFormData({...formData, horizon: +e.target.value})} /></label>
        <button type="submit">Generate Plan</button>
      </form>
      {error && <div className="error">{error}</div>}
      {result && (
        <div className="result">
          <p>Risk Profile: {result.risk_profile}</p>
          <p>Risk Score: {result.risk_score}/10</p>
        </div>
      )}
    </section>
  )
}

export default GoalPlanner