import { useEffect, useState } from 'react'
import { fetchHealthStatus } from './services/api'

function App() {
  const [apiStatus, setApiStatus] = useState<string>('檢查中...')

  useEffect(() => {
    fetchHealthStatus()
      .then((data) => {
        setApiStatus(`${data.app} v${data.version} - ${data.status}`)
      })
      .catch(() => {
        setApiStatus('無法連線至後端 API')
      })
  }, [])

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>台股儀表板</h1>
      <p>後端 API 狀態：{apiStatus}</p>
    </div>
  )
}

export default App
