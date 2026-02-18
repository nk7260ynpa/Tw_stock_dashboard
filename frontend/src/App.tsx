import { useEffect, useState } from 'react'
import './App.css'

interface Tool {
  id: string
  name: string
  description: string
  icon: string
}

function App() {
  const [tools, setTools] = useState<Tool[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/v1/tools')
      .then((res) => res.json())
      .then((data) => {
        setTools(data.tools)
        setLoading(false)
      })
      .catch(() => {
        setLoading(false)
      })
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">台股儀表板</h1>
        <p className="app-subtitle">整合台股工具的統一入口</p>
      </header>
      <main className="app-main">
        {loading ? (
          <p className="loading">載入中...</p>
        ) : (
          <div className="launchpad-grid">
            {tools.map((tool) => (
              <div key={tool.id} className="tool-card">
                <span className="tool-icon">{tool.icon}</span>
                <h3 className="tool-name">{tool.name}</h3>
                <p className="tool-description">{tool.description}</p>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
