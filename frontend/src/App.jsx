import { useEffect, useState } from 'react'
import LaunchPad from './components/LaunchPad'
import './App.css'

function App() {
  const [tools, setTools] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTool, setActiveTool] = useState(null)

  useEffect(() => {
    fetch('/api/tools')
      .then((res) => res.json())
      .then((data) => {
        setTools(data)
        setLoading(false)
      })
      .catch(() => {
        setLoading(false)
      })
  }, [])

  if (activeTool) {
    return (
      <div className="app-embed">
        <header className="embed-header">
          <button className="back-btn" onClick={() => setActiveTool(null)}>
            ← 返回儀表板
          </button>
          <span className="embed-title">{activeTool.icon} {activeTool.name}</span>
        </header>
        <iframe
          className="embed-frame"
          src={activeTool.url}
          title={activeTool.name}
        />
      </div>
    )
  }

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
          <LaunchPad tools={tools} onSelect={setActiveTool} />
        )}
      </main>
    </div>
  )
}

export default App
