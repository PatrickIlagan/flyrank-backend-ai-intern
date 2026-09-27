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

export interface WorkflowStep {
  node_id: string
  node_title: string
  prompt: string
  decision: 'YES' | 'NO'
  reason: string
  timestamp: string
}

export interface WorkflowRun {
  id: string
  status: 'running' | 'completed' | 'failed'
  context: string
  active_node_id: string | null
  active_edge_id: string | null
  steps: WorkflowStep[]
  created_at: string
  completed_at: string | null
}
