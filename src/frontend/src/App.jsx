import React, { useState, useEffect } from 'react'
import GoalPlanner from './components/GoalPlanner.jsx'
import PortfolioView from './components/PortfolioView.jsx'
import ResearchPanel from './components/ResearchPanel.jsx'
import TradeForm from './components/TradeForm.jsx'
import Sidebar from './components/Sidebar.jsx'
import './main.css'

function App() {
  const [activeTab, setActiveTab] = useState('goals')
  const [config, setConfig] = useState({
    trd_env: 'SIMULATE',
    security_firm: 'FUTUSG',
    host: '127.0.0.1',
    port: 11111,
  })
  const [connected, setConnected] = useState(false)

  const tabs = [
    { id: 'goals', label: '🎯 Goal Planner', component: GoalPlanner },
    { id: 'portfolio', label: '💼 Portfolio Health', component: PortfolioView },
    { id: 'research', label: '🔍 Market Research', component: ResearchPanel },
    { id: 'trade', label: '💱 Trade Execution', component: TradeForm },
  ]

  const ActiveComponent = tabs.find(t => t.id === activeTab)?.component || GoalPlanner

  return (
    <div className="app">
      <Sidebar config={config} setConfig={setConfig} connected={connected} setConnected={setConnected} />
      <main className="main-content">
        <h1>📈 Moomoo Investment Agent</h1>
        {!connected && (
          <div className="warning">👈 Configure your trading environment in the sidebar and connect to OpenD</div>
        )}
        <div className="tabs">
          {tabs.map(tab => (
            <button 
              key={tab.id} 
              className={activeTab === tab.id ? 'active' : ''}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <ActiveComponent connected={connected} config={config} />
      </main>
    </div>
  )
}

export default App