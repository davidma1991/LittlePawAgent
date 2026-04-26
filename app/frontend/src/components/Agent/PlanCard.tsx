import type { PlanStep } from '@/types'
import { CheckCircle2, Circle, Clock, XCircle, ListTodo } from 'lucide-react'

interface PlanCardProps {
  steps: PlanStep[]
}

function StepIcon({ status }: { status: PlanStep['status'] }) {
  switch (status) {
    case 'done':
      return <CheckCircle2 size={16} className="text-green-400 shrink-0" />
    case 'running':
      return <Clock size={16} className="text-yellow-400 shrink-0 animate-spin" />
    case 'error':
      return <XCircle size={16} className="text-red-400 shrink-0" />
    default:
      return <Circle size={16} className="text-muted-foreground shrink-0" />
  }
}

export function PlanCard({ steps }: PlanCardProps) {
  return (
    <div className="rounded-lg border border-border bg-secondary/50 overflow-hidden">
      <div className="flex items-center gap-2 px-3 py-2 border-b border-border">
        <ListTodo size={14} className="text-blue-400" />
        <span className="text-xs font-medium text-muted-foreground">Execution Plan</span>
        <span className="ml-auto text-xs text-muted-foreground">
          {steps.filter(s => s.status === 'done').length}/{steps.length} done
        </span>
      </div>
      <div className="p-3 space-y-2">
        {steps.map((step, idx) => (
          <div key={step.id} className="flex items-start gap-2">
            <StepIcon status={step.status} />
            <div className="flex-1 min-w-0">
              <span className="text-xs text-muted-foreground mr-1.5 font-mono">{idx + 1}.</span>
              <span className={`text-xs ${step.status === 'done' ? 'text-muted-foreground line-through' : 'text-foreground'}`}>
                {step.description}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
