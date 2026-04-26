import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import type { Message } from '@/types'

interface ChatWindowProps {
  messages: Message[]
  isLoading: boolean
  onSend: (message: string) => void
  onCancel: () => void
}

export function ChatWindow({ messages, isLoading, onSend, onCancel }: ChatWindowProps) {
  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} />
      <MessageInput
        onSend={onSend}
        onCancel={onCancel}
        isLoading={isLoading}
      />
    </div>
  )
}
