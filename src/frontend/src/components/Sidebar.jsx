import React, { useState } from 'react'

function Sidebar({ config, setConfig, connected, setConnected }) {
  const [loading, setLoading] = useState(false)

  const connect = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })
      const data = await res.json()
      if (data.success) setConnected(true)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  const handleEnvChange = async (e) => {
    const val = e.target.value
    setConfig({ ...config, trd_env: val })
    // Persist environment selection
    try {
      await fetch('/api/set-env/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ trd_env: val })
      })
    } catch (err) {
      console.error('Failed to set env:', err)
    }
  }

  return (
    <aside className="sidebar">
      <h2>📊 Moomoo Agent</h2>
      <div className="config-section">
        <label>Trading Mode</label>
        <select value={config.trd_env} onChange={handleEnvChange}>
          <option value="SIMULATE">Paper Trading (SIMULATE)</option>
          <option value="REAL">Live Trading (REAL)</option>
        </select>
        <label>Security Firm</label>
        <select value={config.security_firm} onChange={e => setConfig({...config, security_firm: e.target.value})}>
          <option value="FUTUSG">Futu SG</option>
          <option value="FUTUSECURITIES">Futu US</option>
        </select>
        <label>OpenD Host</label>
        <input value={config.host} onChange={e => setConfig({...config, host: e.target.value})} />
        <label>OpenD Port</label>
        <input type="number" value={config.port} onChange={e => setConfig({...config, port: +e.target.value})} />
        <button onClick={connect} disabled={loading}>
          {loading ? 'Connecting...' : connected ? '✅ Connected' : 'Connect to OpenD'}
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
