import { useState } from 'react'
import type { ToolCall } from '@/types'
import { ChevronDown, ChevronRight, Loader2, CheckCircle2, XCircle, Wrench } from 'lucide-react'

interface ToolCallCardProps {
  toolCall: ToolCall
}

const TOOL_ICONS: Record<string, string> = {
  web_search: '🔍',
  read_file: '📄',
  write_file: '✏️',
  python_exec: '🐍',
  bash_exec: '💻',
  browser_use: '🌐',
}

export function ToolCallCard({ toolCall }: ToolCallCardProps) {
  const [expanded, setExpanded] = useState(false)
  const icon = TOOL_ICONS[toolCall.tool] || '🔧'
  const isRunning = toolCall.status === 'running'
  const isError = toolCall.status === 'error'

  return (
    <div className={`rounded-lg border overflow-hidden ${isError ? 'border-red-800' : 'border-border'} bg-secondary/30`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 w-full px-3 py-2 text-left hover:bg-secondary transition-colors"
      >
        <span className="text-sm shrink-0">{icon}</span>
        <span className="text-xs font-mono font-medium text-foreground shrink-0">{toolCall.tool}</span>
        <span className="text-xs text-muted-foreground truncate flex-1 text-left">
          {formatInputPreview(toolCall.input)}
        </span>
        <div className="shrink-0 flex items-center gap-1.5">
          {isRunning ? (
            <Loader2 size={13} className="text-yellow-400 animate-spin" />
          ) : isError ? (
            <XCircle size={13} className="text-red-400" />
          ) : (
            <CheckCircle2 size={13} className="text-green-400" />
          )}
          {expanded ? (
            <ChevronDown size={14} className="text-muted-foreground" />
          ) : (
            <ChevronRight size={14} className="text-muted-foreground" />
          )}
        </div>
      </button>

      {expanded && (
        <div className="border-t border-border divide-y divide-border">
          <div className="px-3 py-2">
            <p className="text-xs font-medium text-muted-foreground mb-1.5 flex items-center gap-1">
              <Wrench size={11} /> Input
            </p>
            <pre className="text-xs text-foreground whitespace-pre-wrap font-mono bg-background/50 rounded p-2 overflow-x-auto">
              {JSON.stringify(toolCall.input, null, 2)}
            </pre>
          </div>
          {(toolCall.output !== undefined || toolCall.error) && (
            <div className="px-3 py-2">
              <p className={`text-xs font-medium mb-1.5 ${isError ? 'text-red-400' : 'text-muted-foreground'}`}>
                {isError ? '✗ Error' : '✓ Output'}
              </p>
              <pre className={`text-xs whitespace-pre-wrap font-mono bg-background/50 rounded p-2 overflow-x-auto max-h-48 ${isError ? 'text-red-300' : 'text-foreground'}`}>
                {isError
                  ? toolCall.error
                  : typeof toolCall.output === 'string'
                    ? toolCall.output
                    : JSON.stringify(toolCall.output, null, 2)
                }
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function formatInputPreview(input: Record<string, unknown>): string {
  const entries = Object.entries(input)
  if (entries.length === 0) return '{}'
  const [, val] = entries[0]
  const strVal = typeof val === 'string' ? val : JSON.stringify(val)
  const preview = strVal.length > 60 ? strVal.slice(0, 60) + '…' : strVal
  return entries.length === 1 ? preview : `${preview} (+${entries.length - 1} more)`
}
