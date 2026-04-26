import type { McpConfig } from '@/types'

interface McpServerListProps {
  config: McpConfig | null
  status: Record<string, string>
}

function StatusBadge({ status }: { status: string }) {
  if (status === 'connected') {
    return <span className="w-2 h-2 rounded-full bg-green-400 shrink-0" title="Connected" />
  }
  if (status === 'disabled') {
    return <span className="w-2 h-2 rounded-full bg-muted-foreground/40 shrink-0" title="Disabled" />
  }
  return <span className="w-2 h-2 rounded-full bg-red-400 shrink-0" title={status} />
}

export function McpServerList({ config, status }: McpServerListProps) {
  const servers = config?.mcpServers || {}

  return (
    <div>
      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block mb-2">
        MCP Servers
      </label>
      <div className="space-y-1">
        {Object.entries(servers).map(([name, cfg]) => {
          const serverStatus = status[name] || (cfg.enabled ? 'connecting' : 'disabled')
          return (
            <div key={name} className="flex items-center gap-2 px-2 py-1.5 rounded-md">
              <StatusBadge status={serverStatus} />
              <span className="text-xs font-mono text-foreground flex-1 truncate">{name}</span>
              {!cfg.enabled && (
                <span className="text-xs text-muted-foreground">(off)</span>
              )}
            </div>
          )
        })}
        {Object.keys(servers).length === 0 && (
          <p className="text-xs text-muted-foreground px-2 py-1">No MCP servers configured</p>
        )}
      </div>
    </div>
  )
}
