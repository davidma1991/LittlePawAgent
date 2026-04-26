import type { Message } from '@/types'
import { ThinkingCard } from '@/components/Agent/ThinkingCard'
import { PlanCard } from '@/components/Agent/PlanCard'
import { ToolCallCard } from '@/components/Agent/ToolCallCard'
import { Bot, User } from 'lucide-react'

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex gap-3 justify-end">
        <div className="max-w-[75%] rounded-2xl rounded-tr-sm bg-primary text-primary-foreground px-4 py-3 text-sm leading-relaxed">
          <pre className="whitespace-pre-wrap font-sans">{message.content}</pre>
        </div>
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0 mt-1">
          <User size={16} className="text-primary-foreground" />
        </div>
      </div>
    )
  }

  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 rounded-full bg-secondary border border-border flex items-center justify-center shrink-0 mt-1">
        <Bot size={16} className="text-muted-foreground" />
      </div>
      <div className="flex-1 space-y-2 min-w-0">
        {message.thinking && (
          <ThinkingCard content={message.thinking} isStreaming={message.isStreaming} />
        )}
        {message.plan && message.plan.length > 0 && (
          <PlanCard steps={message.plan} />
        )}
        {message.toolCalls && message.toolCalls.map(tc => (
          <ToolCallCard key={tc.call_id} toolCall={tc} />
        ))}
        {message.content && (
          <div className="rounded-2xl rounded-tl-sm bg-secondary border border-border px-4 py-3 text-sm leading-relaxed text-foreground">
            <pre className="whitespace-pre-wrap font-sans">{message.content}</pre>
            {message.isStreaming && (
              <span className="inline-block w-2 h-4 bg-foreground opacity-70 animate-pulse ml-0.5 align-middle" />
            )}
          </div>
        )}
        {message.error && (
          <div className="rounded-lg bg-red-900/30 border border-red-800 px-4 py-3 text-sm text-red-300">
            Error: {message.error}
          </div>
        )}
        {message.isStreaming && !message.content && !message.thinking && !message.plan?.length && !message.toolCalls?.length && (
          <div className="rounded-2xl rounded-tl-sm bg-secondary border border-border px-4 py-3">
            <div className="flex gap-1">
              <span className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
