import { useEffect, useState } from 'react'
import LaunchPad from './components/LaunchPad'
import './App.css'

function App() {
  const [tools, setTools] = useState([])
  const [loading, setLoading] = useState(true)

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
          <LaunchPad tools={tools} />
        )}
      </main>
    </div>
  )
}

export default App
