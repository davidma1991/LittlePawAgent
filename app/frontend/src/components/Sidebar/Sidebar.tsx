import { Trash2 } from 'lucide-react'
import { ModelSelector } from './ModelSelector'
import { PlanModeToggle } from './PlanModeToggle'
import { ToolList } from './ToolList'
import { McpServerList } from './McpServerList'
import type { ToolInfo, McpConfig } from '@/types'

interface SidebarProps {
  models: string[]
  selectedModel: string
  onModelSelect: (model: string) => void
  mode: 'react' | 'plan_execute'
  onModeChange: (mode: 'react' | 'plan_execute') => void
  tools: ToolInfo[]
  onToolToggle: (name: string, enabled: boolean) => void
  mcpConfig: McpConfig | null
  mcpStatus: Record<string, string>
  onRefresh: () => void
  onClear: () => void
  isLoading: boolean
}

export function Sidebar({
  models, selectedModel, onModelSelect,
  mode, onModeChange,
  tools, onToolToggle,
  mcpConfig, mcpStatus,
  onRefresh, onClear, isLoading,
}: SidebarProps) {
  return (
    <div className="w-64 shrink-0 bg-secondary/30 border-r border-border flex flex-col h-full">
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <span className="text-xl">🐾</span>
          <span className="font-semibold text-sm text-foreground">LittlePaw Agent</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        <ModelSelector
          models={models}
          selectedModel={selectedModel}
          onSelect={onModelSelect}
          onRefresh={onRefresh}
          isLoading={isLoading}
        />
        <PlanModeToggle mode={mode} onChange={onModeChange} />
        <ToolList tools={tools} onToggle={onToolToggle} />
        <McpServerList config={mcpConfig} status={mcpStatus} />
      </div>

      <div className="p-4 border-t border-border">
        <button
          onClick={onClear}
          className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-xs text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
        >
          <Trash2 size={13} />
          Clear conversation
        </button>
      </div>
    </div>
  )
}
