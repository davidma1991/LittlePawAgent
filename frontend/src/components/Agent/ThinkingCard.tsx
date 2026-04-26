import { useState } from 'react'
import { ChevronDown, ChevronRight, Brain } from 'lucide-react'

interface ThinkingCardProps {
  content: string
  isStreaming?: boolean
}

export function ThinkingCard({ content, isStreaming }: ThinkingCardProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="rounded-lg border border-border bg-secondary/50 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 w-full px-3 py-2 text-left hover:bg-secondary transition-colors"
      >
        <Brain size={14} className="text-purple-400 shrink-0" />
        <span className="text-xs font-medium text-muted-foreground flex-1">
          {isStreaming ? 'Thinking...' : 'Thought process'}
        </span>
        {isStreaming && (
          <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse shrink-0" />
        )}
        {expanded ? (
          <ChevronDown size={14} className="text-muted-foreground shrink-0" />
        ) : (
          <ChevronRight size={14} className="text-muted-foreground shrink-0" />
        )}
      </button>
      {expanded && (
        <div className="px-3 pb-3 border-t border-border">
          <pre className="text-xs text-muted-foreground whitespace-pre-wrap font-sans pt-2 leading-relaxed">
            {content}
          </pre>
        </div>
      )}
    </div>
  )
}
