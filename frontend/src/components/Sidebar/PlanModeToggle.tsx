import { Zap, BrainCircuit } from 'lucide-react'

interface PlanModeToggleProps {
  mode: 'react' | 'plan_execute'
  onChange: (mode: 'react' | 'plan_execute') => void
}

export function PlanModeToggle({ mode, onChange }: PlanModeToggleProps) {
  return (
    <div>
      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block mb-2">
        Mode
      </label>
      <div className="flex rounded-lg border border-border overflow-hidden">
        <button
          onClick={() => onChange('react')}
          className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-medium transition-colors ${
            mode === 'react'
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-muted-foreground hover:text-foreground'
          }`}
        >
          <Zap size={13} />
          ReAct
        </button>
        <button
          onClick={() => onChange('plan_execute')}
          className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-medium transition-colors border-l border-border ${
            mode === 'plan_execute'
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-muted-foreground hover:text-foreground'
          }`}
        >
          <BrainCircuit size={13} />
          Plan
        </button>
      </div>
    </div>
  )
}
