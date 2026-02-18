const API_BASE_URL = '/api'

interface HealthResponse {
  status: string
  app: string
  version: string
}

interface Tool {
  id: string
  name: string
  description: string
  icon: string
}

/** 取得後端健康檢查狀態。 */
export async function fetchHealthStatus(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/../health`)
  if (!response.ok) {
    throw new Error(`API 錯誤: ${response.status}`)
  }
  return response.json()
}

/** 取得工具清單。 */
export async function fetchTools(): Promise<Tool[]> {
  const response = await fetch(`${API_BASE_URL}/v1/tools`)
  if (!response.ok) {
    throw new Error(`API 錯誤: ${response.status}`)
  }
  const data = await response.json()
  return data.tools
}
