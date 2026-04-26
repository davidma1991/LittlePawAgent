import { useEffect, useRef } from 'react'
import type { Message } from '@/types'
import { MessageBubble } from './MessageBubble'

interface MessageListProps {
  messages: Message[]
}

export function MessageList({ messages }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-center px-4">
        <div>
          <div className="text-4xl mb-4">🐾</div>
          <h2 className="text-lg font-semibold text-foreground mb-2">LittlePaw Agent</h2>
          <p className="text-sm text-muted-foreground max-w-sm">
            A local AI agent powered by Ollama. Ask me anything — I can search the web, run code, browse websites, and more.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {messages.map(message => (
          <MessageBubble key={message.id} message={message} />
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
