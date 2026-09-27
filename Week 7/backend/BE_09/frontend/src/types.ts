export interface DecisionNodeData {
  title: string
  prompt: string
  status?: 'idle' | 'running' | 'completed_yes' | 'completed_no' | 'skipped'
  lastReason?: string
  [key: string]: unknown
}

export interface WorkflowEdgeData {
  label?: 'YES' | 'NO'
  isActive?: boolean
  [key: string]: unknown
}
