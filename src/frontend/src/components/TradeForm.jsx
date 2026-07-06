import React, { useState } from 'react'

function TradeForm({ connected, config }) {
  const [order, setOrder] = useState({ code: 'US.AAPL', qty: 100, price: 200 })
  const [approved, setApproved] = useState(false)
  const [password, setPassword] = useState('')
  const [passwordVerified, setPasswordVerified] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const verifyPassword = async () => {
    try {
      const res = await fetch('/api/verify-password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      })
      const data = await res.json()
      if (data.success) {
        setPasswordVerified(true)
        setError('')
      } else {
        setError(data.message || 'Password verification failed')
      }
    } catch (e) {
      setError('Verification failed: ' + e.message)
    }
  }

  const submit = async () => {
    setError('')
    try {
      const res = await fetch('/api/trade/execute/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...order, trd_env: config.trd_env, user_approved: approved })
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to execute trade')
      }
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <section>
      <h2>💱 Trade Execution</h2>
      <div className="form-group">
        <label>Code: <input value={order.code} onChange={e => setOrder({...order, code: e.target.value})} /></label>
        <label>Quantity: <input type="number" value={order.qty} onChange={e => setOrder({...order, qty: +e.target.value})} /></label>
        <label>Price: <input type="number" value={order.price} onChange={e => setOrder({...order, price: +e.target.value})} /></label>
        
        {config.trd_env === 'REAL' && (
          <div>
            {!passwordVerified ? (
              <>
                <label>Trade Password: <input type="password" value={password} onChange={e => setPassword(e.target.value)} /></label>
                <button onClick={verifyPassword}>Verify Password</button>
              </>
            ) : (
              <div className="status verified">✅ Password Verified - REAL Trading Enabled</div>
            )}
            {passwordVerified && (
              <label>
                <input type="checkbox" checked={approved} onChange={e => setApproved(e.target.checked)} />
                I approve this trade
              </label>
            )}
          </div>
        )}
        {config.trd_env === 'SIMULATE' && (
          <label>
            <input type="checkbox" checked={approved} onChange={e => setApproved(e.target.checked)} />
            I approve this trade (auto-approved in SIMULATE mode)
          </label>
        )}
        <button onClick={submit} disabled={config.trd_env === 'REAL' && !passwordVerified}>
          {config.trd_env === 'REAL' && !passwordVerified ? 'Verify Password First' : 'Execute Trade'}
        </button>
      </div>
      {error && <div className="error">{error}</div>}
      {result && (
        <div className="result">
          {result.status === 'success' ? '✅ Order placed!' : `❌ ${result.reason || result.status}`}
          {result.order_id && <p>Order ID: {result.order_id}</p>}
        </div>
      )}
    </section>
  )
}

export default TradeForm
