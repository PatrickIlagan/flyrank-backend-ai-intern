import { memo } from 'react'
import { Handle, Position, type NodeProps, type Node } from '@xyflow/react'
import { Sparkles, CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import type { DecisionNodeData } from '../types'

export type DecisionNodeType = Node<DecisionNodeData, 'decisionNode'>

function DecisionNodeComponent({ data, selected }: NodeProps<DecisionNodeType>) {
  const title = (data?.title as string) || 'AI Decision Node'
  const prompt = (data?.prompt as string) || 'Evaluate decision criteria...'
  const status = (data?.status as string) || 'idle'

  return (
    <div
      className={`w-72 rounded-xl bg-gray-900/95 border transition-all duration-200 shadow-xl backdrop-blur-md ${
        selected
          ? 'border-indigo-500 ring-2 ring-indigo-500/40 shadow-indigo-500/20'
          : status === 'running'
          ? 'border-blue-500 ring-2 ring-blue-500/40 animate-pulse'
          : status === 'completed_yes'
          ? 'border-emerald-500 ring-1 ring-emerald-500/30'
          : status === 'completed_no'
          ? 'border-amber-500 ring-1 ring-amber-500/30'
          : 'border-gray-800 hover:border-gray-700'
      }`}
    >
      {/* Target Handle (Top Input) */}
      <Handle
        type="target"
        position={Position.Top}
        id="in"
        className="!w-3.5 !h-3.5 !bg-gray-700 !border-2 !border-gray-900 hover:!bg-indigo-400 transition"
      />

      {/* Node Header */}
      <div className="px-3.5 py-2.5 border-b border-gray-800/80 flex items-center justify-between bg-gray-950/40 rounded-t-xl">
        <div className="flex items-center gap-2 overflow-hidden">
          <div className="w-5 h-5 rounded-md bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0">
            <Sparkles className="w-3 h-3" />
          </div>
          <span className="text-xs font-semibold text-gray-200 truncate tracking-wide">
            {title}
          </span>
        </div>

        {/* Status Badge */}
        {status === 'running' && (
          <span className="flex items-center gap-1 text-[10px] font-medium text-blue-400 bg-blue-950/60 px-2 py-0.5 rounded-full border border-blue-800/50">
            <Loader2 className="w-2.5 h-2.5 animate-spin" /> Evaluating
          </span>
        )}
        {status === 'completed_yes' && (
          <span className="flex items-center gap-1 text-[10px] font-medium text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-800/50">
            <CheckCircle2 className="w-2.5 h-2.5" /> YES
          </span>
        )}
        {status === 'completed_no' && (
          <span className="flex items-center gap-1 text-[10px] font-medium text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded-full border border-amber-800/50">
            <XCircle className="w-2.5 h-2.5" /> NO
          </span>
        )}
      </div>

      {/* Node Body (Prompt / Question) */}
      <div className="p-3.5">
        <p className="text-xs text-gray-300 leading-relaxed font-normal bg-gray-950/60 p-2.5 rounded-lg border border-gray-800/60 select-none">
          "{prompt}"
        </p>
      </div>

      {/* Node Footer: Dual YES / NO Output Handles */}
      <div className="px-3.5 pb-3 pt-1 flex items-center justify-between border-t border-gray-800/50 text-[11px] font-semibold">
        {/* Left Side: YES Handle */}
        <div className="relative flex items-center gap-1.5 text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50" />
          <span>YES</span>
          <Handle
            type="source"
            position={Position.Bottom}
            id="yes"
            className="!w-3.5 !h-3.5 !bg-emerald-500 !border-2 !border-gray-900 hover:!bg-emerald-300 transition !-bottom-1.5"
            style={{ left: '25%' }}
          />
        </div>

        {/* Right Side: NO Handle */}
        <div className="relative flex items-center gap-1.5 text-amber-400">
          <span>NO</span>
          <span className="w-2 h-2 rounded-full bg-amber-400 shadow-sm shadow-amber-400/50" />
          <Handle
            type="source"
            position={Position.Bottom}
            id="no"
            className="!w-3.5 !h-3.5 !bg-amber-500 !border-2 !border-gray-900 hover:!bg-amber-300 transition !-bottom-1.5"
            style={{ left: '75%' }}
          />
        </div>
      </div>
    </div>
  )
}

export const DecisionNode = memo(DecisionNodeComponent)
