import React, { useState } from 'react'

function PortfolioView({ connected, config }) {
  const [health, setHealth] = useState(null)
  const [error, setError] = useState('')

  const analyze = async () => {
    setError('')
    setHealth(null)
    try {
      const res = await fetch(`/api/portfolio/health/?trd_env=${config.trd_env}`)
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to connect to backend')
      }
      const data = await res.json()
      setHealth(data)
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <section>
      <h2>💼 Portfolio Health</h2>
      <button onClick={analyze}>Analyze Portfolio</button>
      {error && <div className="error">{error}</div>}
      {health && (
        <div className="result">
          <p>Diversification Score: {health.diversification_score}</p>
          <p>Total Positions: {health.total_positions}</p>
          {health.analysis_status && <p>Status: {health.analysis_status}</p>}
        </div>
      )}
    </section>
  )
}

export default PortfolioView