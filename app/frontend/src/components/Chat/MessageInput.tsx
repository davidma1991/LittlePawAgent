import { useState, useRef, KeyboardEvent } from 'react'
import { Send, Square } from 'lucide-react'

interface MessageInputProps {
  onSend: (message: string) => void
  onCancel: () => void
  isLoading: boolean
  disabled?: boolean
}

export function MessageInput({ onSend, onCancel, isLoading, disabled }: MessageInputProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    const trimmed = value.trim()
    if (!trimmed || isLoading) return
    onSend(trimmed)
    setValue('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = () => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 200) + 'px'
  }

  return (
    <div className="border-t border-border p-4">
      <div className="flex gap-3 items-end max-w-4xl mx-auto">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          disabled={disabled}
          placeholder="Type your message... (Shift+Enter for newline)"
          rows={1}
          className="flex-1 resize-none rounded-lg border border-border bg-secondary px-4 py-3 text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 min-h-[48px] max-h-[200px]"
        />
        {isLoading ? (
          <button
            onClick={onCancel}
            className="flex items-center gap-2 px-4 py-3 rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors text-sm font-medium shrink-0"
          >
            <Square size={16} />
            Stop
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={!value.trim() || disabled}
            className="flex items-center gap-2 px-4 py-3 rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
          >
            <Send size={16} />
            Send
          </button>
        )}
      </div>
    </div>
  )
}
