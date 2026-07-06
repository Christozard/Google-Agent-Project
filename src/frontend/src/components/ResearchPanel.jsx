import React, { useState } from 'react'

function ResearchPanel({ connected, config }) {
  const [tickers, setTickers] = useState('US.AAPL, US.MSFT')
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const research = async () => {
    setError('')
    setResults(null)
    setLoading(true)
    const tickerList = tickers.split(',').map(t => t.trim())
    try {
      const res = await fetch('/api/research/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tickers: tickerList })
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to connect to backend')
      }
      const data = await res.json()
      setResults(data.rankings || data.research_results)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h2>🔍 Market Research</h2>
      <textarea value={tickers} onChange={e => setTickers(e.target.value)} placeholder="US.AAPL, US.MSFT" />
      <button onClick={research} disabled={loading}>
        {loading ? 'Loading...' : 'Research'}
      </button>
      {error && <div className="error">{error}</div>}
      {results && (
        <div className="results">
          {results.map((r, i) => (
            <div key={i} className="result-card">
              <div className="card-header">
                <strong>{r.code}</strong>
                <span className={`badge ${r.recommendation?.toLowerCase()}`}>{r.recommendation}</span>
              </div>
              <div className="stats-grid">
                <div>Price: ${r.last_price?.toFixed(2)}</div>
                <div>P/E: {r.pe_ratio?.toFixed(2) || 'N/A'}</div>
                <div>P/B: {r.pb_ratio?.toFixed(2) || 'N/A'}</div>
                <div>Volume: {r.volume?.toLocaleString()}</div>
                <div>Momentum: {r.momentum ? `${r.momentum > 0 ? '↑' : '↓'} ${Math.abs(r.momentum).toFixed(1)}%` : 'N/A'}</div>
              </div>
              {r.news && r.news.length > 0 && (
                <div className="news-section">
                  <h4>📰 Related News</h4>
                  {r.news.map((n, idx) => (
                    <div key={idx} className="news-item">
                      <a href={n.url} target="_blank" rel="noopener noreferrer">{n.title}</a>
                      {n.summary && <p className="news-summary">{n.summary}</p>}
                      <small>{n.source} - {n.time}</small>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

export default ResearchPanel
