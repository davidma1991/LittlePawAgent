import { RefreshCw } from 'lucide-react'

interface ModelSelectorProps {
  models: string[]
  selectedModel: string
  onSelect: (model: string) => void
  onRefresh: () => void
  isLoading: boolean
}

export function ModelSelector({ models, selectedModel, onSelect, onRefresh, isLoading }: ModelSelectorProps) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Model
        </label>
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="p-1 rounded hover:bg-secondary transition-colors disabled:opacity-50"
          title="Refresh models"
        >
          <RefreshCw size={12} className={`text-muted-foreground ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>
      <select
        value={selectedModel}
        onChange={e => onSelect(e.target.value)}
        className="w-full rounded-lg border border-border bg-secondary px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
      >
        {models.length === 0 && (
          <option value={selectedModel}>{selectedModel}</option>
        )}
        {models.map(m => (
          <option key={m} value={m}>{m}</option>
        ))}
      </select>
    </div>
  )
}
