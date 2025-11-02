import { useEffect, useState } from 'react'

function App() {
  const [message, setMessage] = useState('加载中...')

  useEffect(() => {
    const base =
      import.meta.env.VITE_API_URL ||
      import.meta.env.VITE_API_BASE_URL ||
      'http://localhost:8000'

    fetch(`${base}/api/v1/health`)
      .then((res) => (res.ok ? res.json() : Promise.reject(res.statusText)))
      .then((data) => setMessage(data?.status ?? 'ok'))
      .catch(() => setMessage('后端未启动或无法访问'))
  }, [])

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', padding: 24 }}>
      <h1>Vite + React + FastAPI</h1>
      <p>后端健康检查: {message}</p>
      <p>环境变量优先使用 VITE_API_URL（兼容 VITE_API_BASE_URL）。</p>
    </div>
  )
}

export default App
