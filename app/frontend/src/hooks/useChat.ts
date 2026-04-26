import { useState, useCallback, useRef } from 'react'
import type { Message, StreamEvent, PlanStep, ToolCall } from '@/types'
import { streamChat } from '@/lib/api'

function generateId() {
  return Math.random().toString(36).slice(2)
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const cancelRef = useRef<(() => void) | null>(null)

  const sendMessage = useCallback((
    userMessage: string,
    model: string,
    mode: 'react' | 'plan_execute',
  ) => {
    if (isLoading) return

    const userMsg: Message = {
      id: generateId(),
      role: 'user',
      content: userMessage,
    }

    const assistantId = generateId()
    const assistantMsg: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      isStreaming: true,
      toolCalls: [],
    }

    setMessages(prev => [...prev, userMsg, assistantMsg])
    setIsLoading(true)

    const history = messages
      .filter(m => !m.isStreaming)
      .map(m => ({ role: m.role, content: m.content }))

    const cancel = streamChat({
      message: userMessage,
      model,
      mode,
      conversationHistory: history,
      onEvent: (event: StreamEvent) => {
        setMessages(prev => prev.map(m => {
          if (m.id !== assistantId) return m

          switch (event.type) {
            case 'thinking':
              return { ...m, thinking: (m.thinking || '') + event.content }

            case 'plan':
              return { ...m, plan: event.steps as PlanStep[] }

            case 'plan_step_start':
              return {
                ...m,
                plan: m.plan?.map(s =>
                  s.id === event.step_id ? { ...s, status: 'running' as const } : s
                ),
              }

            case 'plan_step_done':
              return {
                ...m,
                plan: m.plan?.map(s =>
                  s.id === event.step_id ? { ...s, status: 'done' as const } : s
                ),
              }

            case 'tool_start': {
              const newCall: ToolCall = {
                call_id: event.call_id!,
                tool: event.tool!,
                input: event.input as Record<string, unknown>,
                status: 'running',
              }
              return { ...m, toolCalls: [...(m.toolCalls || []), newCall] }
            }

            case 'tool_result':
              return {
                ...m,
                toolCalls: m.toolCalls?.map(tc =>
                  tc.call_id === event.call_id
                    ? { ...tc, output: event.output, error: event.error, status: event.error ? 'error' as const : 'done' as const }
                    : tc
                ),
              }

            case 'token':
              return { ...m, content: m.content + (event.content || '') }

            default:
              return m
          }
        }))
      },
      onError: (error: string) => {
        setMessages(prev => prev.map(m =>
          m.id === assistantId
            ? { ...m, isStreaming: false, error }
            : m
        ))
        setIsLoading(false)
      },
      onDone: () => {
        setMessages(prev => prev.map(m =>
          m.id === assistantId ? { ...m, isStreaming: false } : m
        ))
        setIsLoading(false)
      },
    })

    cancelRef.current = cancel
  }, [messages, isLoading])

  const cancelStream = useCallback(() => {
    cancelRef.current?.()
    setIsLoading(false)
    setMessages(prev => prev.map(m =>
      m.isStreaming ? { ...m, isStreaming: false } : m
    ))
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  return { messages, isLoading, sendMessage, cancelStream, clearMessages }
}
