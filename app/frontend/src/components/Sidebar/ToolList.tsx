import type { ToolInfo } from '@/types'

interface ToolListProps {
  tools: ToolInfo[]
  onToggle: (name: string, enabled: boolean) => void
}

const TOOL_ICONS: Record<string, string> = {
  web_search: '🔍',
  read_file: '📄',
  write_file: '✏️',
  python_exec: '🐍',
  bash_exec: '💻',
  browser_use: '🌐',
}

export function ToolList({ tools, onToggle }: ToolListProps) {
  const builtins = tools.filter(t => t.source === 'builtin')
  const mcpTools = tools.filter(t => t.source === 'mcp')

  return (
    <div>
      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block mb-2">
        Tools
      </label>
      <div className="space-y-1">
        {builtins.map(tool => (
          <label key={tool.name} className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-secondary cursor-pointer">
            <input
              type="checkbox"
              checked={tool.enabled}
              onChange={e => onToggle(tool.name, e.target.checked)}
              className="rounded border-border accent-primary"
            />
            <span className="text-sm">{TOOL_ICONS[tool.name] || '🔧'}</span>
            <span className="text-xs text-foreground flex-1 font-mono">{tool.name}</span>
          </label>
        ))}
        {mcpTools.length > 0 && (
          <>
            <div className="pt-1 pb-0.5 px-2 text-xs text-muted-foreground">MCP tools</div>
            {mcpTools.map(tool => (
              <label key={tool.name} className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-secondary cursor-pointer">
                <input
                  type="checkbox"
                  checked={tool.enabled}
                  onChange={e => onToggle(tool.name, e.target.checked)}
                  className="rounded border-border accent-primary"
                />
                <span className="text-sm">🔌</span>
                <span className="text-xs text-foreground flex-1 font-mono truncate">{tool.name}</span>
              </label>
            ))}
          </>
        )}
        {tools.length === 0 && (
          <p className="text-xs text-muted-foreground px-2 py-1">No tools loaded</p>
        )}
      </div>
    </div>
  )
}
