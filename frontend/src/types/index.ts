export interface PlanStep {
  id: string
  description: string
  status: 'pending' | 'running' | 'done' | 'error'
}

export interface ToolCall {
  call_id: string
  tool: string
  input: Record<string, unknown>
  output?: unknown
  error?: string | null
  status: 'running' | 'done' | 'error'
}

export type StreamEventType =
  | 'thinking'
  | 'plan'
  | 'plan_step_start'
  | 'plan_step_done'
  | 'tool_start'
  | 'tool_result'
  | 'token'
  | 'done'
  | 'error'

export interface StreamEvent {
  type: StreamEventType
  content?: string
  steps?: PlanStep[]
  step_id?: string
  summary?: string
  call_id?: string
  tool?: string
  input?: Record<string, unknown>
  output?: unknown
  error?: string | null
  message?: string
}

export type MessageRole = 'user' | 'assistant'

export interface Message {
  id: string
  role: MessageRole
  content: string
  thinking?: string
  plan?: PlanStep[]
  toolCalls?: ToolCall[]
  isStreaming?: boolean
  error?: string
}

export interface ToolInfo {
  name: string
  description: string
  source: string
  enabled: boolean
}

export interface AgentConfig {
  ollama: {
    base_url: string
    default_model: string
  }
  tools: Record<string, { enabled: boolean; [key: string]: unknown }>
}

export interface McpServerConfig {
  enabled: boolean
  transport: 'stdio' | 'http'
  command?: string
  args?: string[]
  url?: string
}

export interface McpConfig {
  mcpServers: Record<string, McpServerConfig>
}
