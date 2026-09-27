import { memo } from 'react'
import {
  BaseEdge,
  EdgeLabelRenderer,
  getBezierPath,
  type EdgeProps,
  type Edge,
  useReactFlow
} from '@xyflow/react'
import { X } from 'lucide-react'
import type { WorkflowEdgeData } from '../types'

export type WorkflowEdgeType = Edge<WorkflowEdgeData, 'workflowEdge'>

function WorkflowEdgeComponent({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  sourceHandleId,
  data,
  style = {}
}: EdgeProps<WorkflowEdgeType>) {
  const { setEdges } = useReactFlow()
  const isYes = sourceHandleId === 'yes' || data?.label === 'YES'

  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition
  })

  const strokeColor = isYes ? '#10b981' : '#f59e0b'

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    setEdges((edges) => edges.filter((edge) => edge.id !== id))
  }

  return (
    <>
      <BaseEdge
        path={edgePath}
        className={data?.isActive ? 'edge-flow-active' : ''}
        style={{
          ...style,
          stroke: strokeColor,
          strokeWidth: data?.isActive ? 3.5 : 2.5,
          filter: data?.isActive ? `drop-shadow(0 0 8px ${strokeColor})` : undefined
        }}
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: 'all'
          }}
          className="group relative flex items-center"
        >
          {/* Label Badge */}
          <div
            className={`px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider shadow-md border transition-all ${
              isYes
                ? 'bg-emerald-950/90 text-emerald-400 border-emerald-800/80 shadow-emerald-950/50'
                : 'bg-amber-950/90 text-amber-400 border-amber-800/80 shadow-amber-950/50'
            } ${data?.isActive ? 'ring-2 ring-white/60 scale-110 shadow-lg' : ''}`}
          >
            {isYes ? 'YES' : 'NO'}
          </div>

          {/* Delete Edge Button on Hover */}
          <button
            onClick={handleDelete}
            title="Delete connection"
            className="absolute -right-5 opacity-0 group-hover:opacity-100 w-4 h-4 rounded-full bg-rose-950 border border-rose-800 text-rose-300 flex items-center justify-center hover:bg-rose-900 transition"
          >
            <X className="w-2.5 h-2.5" />
          </button>
        </div>
      </EdgeLabelRenderer>
    </>
  )
}

export const WorkflowEdge = memo(WorkflowEdgeComponent)
