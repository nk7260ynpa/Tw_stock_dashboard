const API_BASE_URL = '/api'

interface HealthResponse {
  status: string
  app: string
  version: string
}

/** 取得後端健康檢查狀態。 */
export async function fetchHealthStatus(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/../health`)
  if (!response.ok) {
    throw new Error(`API 錯誤: ${response.status}`)
  }
  return response.json()
}

/** 取得 API v1 狀態。 */
export async function fetchApiV1Status(): Promise<{ api_version: string; status: string }> {
  const response = await fetch(`${API_BASE_URL}/v1/status`)
  if (!response.ok) {
    throw new Error(`API 錯誤: ${response.status}`)
  }
  return response.json()
}
