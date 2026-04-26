import type { AgentConfig, McpConfig, ToolInfo, StreamEvent } from '@/types'

const BASE_URL = '/api'

export async function fetchModels(): Promise<string[]> {
  const res = await fetch(`${BASE_URL}/models`)
  if (!res.ok) throw new Error('Failed to fetch models')
  const data = await res.json()
  return data.models as string[]
}

export async function fetchConfig(): Promise<{ agent: AgentConfig; mcp: McpConfig; mcp_status: Record<string, string> }> {
  const res = await fetch(`${BASE_URL}/config`)
  if (!res.ok) throw new Error('Failed to fetch config')
  return res.json()
}

export async function updateConfig(config: { agent?: AgentConfig; mcp?: McpConfig }): Promise<void> {
  const res = await fetch(`${BASE_URL}/config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  if (!res.ok) throw new Error('Failed to update config')
}

export async function fetchTools(): Promise<ToolInfo[]> {
  const res = await fetch(`${BASE_URL}/tools`)
  if (!res.ok) throw new Error('Failed to fetch tools')
  const data = await res.json()
  return data.tools as ToolInfo[]
}

export function streamChat(params: {
  message: string
  model: string
  mode: 'react' | 'plan_execute'
  conversationHistory: Array<{ role: string; content: string }>
  onEvent: (event: StreamEvent) => void
  onError: (error: string) => void
  onDone: () => void
}): () => void {
  const controller = new AbortController()

  ;(async () => {
    try {
      const res = await fetch(`${BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: params.message,
          model: params.model,
          mode: params.mode,
          conversation_history: params.conversationHistory,
        }),
        signal: controller.signal,
      })

      if (!res.ok) {
        params.onError(`HTTP error: ${res.status}`)
        return
      }

      const reader = res.body?.getReader()
      if (!reader) {
        params.onError('No response body')
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            if (!data) continue
            try {
              const event = JSON.parse(data) as StreamEvent
              if (event.type === 'done') {
                params.onDone()
              } else if (event.type === 'error') {
                params.onError(event.message || 'Unknown error')
              } else {
                params.onEvent(event)
              }
            } catch {
              // ignore parse errors
            }
          }
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name !== 'AbortError') {
        params.onError(err.message)
      }
    }
  })()

  return () => controller.abort()
}
