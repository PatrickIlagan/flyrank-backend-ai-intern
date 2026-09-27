import { type Node } from '@xyflow/react'
import { X, Trash2, Edit3, HelpCircle, CheckCircle, XCircle } from 'lucide-react'
import type { DecisionNodeData } from '../types'

interface NodeInspectorProps {
  selectedNode: Node<DecisionNodeData> | null
  onUpdateNode: (nodeId: string, updates: Partial<DecisionNodeData>) => void
  onDeleteNode: (nodeId: string) => void
  onClose: () => void
}

export function NodeInspector({
  selectedNode,
  onUpdateNode,
  onDeleteNode,
  onClose
}: NodeInspectorProps) {
  if (!selectedNode) return null

  const data = selectedNode.data || { title: '', prompt: '' }

  return (
    <aside className="absolute right-4 top-18 bottom-6 w-80 bg-gray-900/95 border border-gray-800 rounded-xl shadow-2xl backdrop-blur-md z-20 flex flex-col overflow-hidden animate-in slide-in-from-right duration-200">
      {/* Inspector Header */}
      <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between bg-gray-950/60">
        <div className="flex items-center gap-2">
          <Edit3 className="w-4 h-4 text-indigo-400" />
          <h2 className="text-xs font-bold text-white uppercase tracking-wider">Node Inspector</h2>
        </div>
        <button
          onClick={onClose}
          className="w-6 h-6 rounded-md hover:bg-gray-800 text-gray-400 hover:text-white flex items-center justify-center transition"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Inspector Form */}
      <div className="p-4 flex-1 overflow-y-auto space-y-4 text-xs">
        {/* Node Identifier */}
        <div>
          <label className="text-[11px] font-semibold text-gray-400 block mb-1">Node ID</label>
          <div className="px-2.5 py-1.5 rounded-lg bg-gray-950 border border-gray-800 font-mono text-gray-300 select-all">
            {selectedNode.id}
          </div>
        </div>

        {/* Title Input */}
        <div>
          <label className="text-[11px] font-semibold text-gray-300 block mb-1">Step Title</label>
          <input
            type="text"
            value={data.title || ''}
            onChange={(e) => onUpdateNode(selectedNode.id, { title: e.target.value })}
            placeholder="e.g. Support Classifier"
            className="w-full px-3 py-2 rounded-lg bg-gray-950 border border-gray-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white placeholder-gray-500 outline-none transition"
          />
        </div>

        {/* Prompt Textarea */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-[11px] font-semibold text-gray-300">Decision Question / Prompt</label>
            <span className="text-[10px] text-indigo-400 flex items-center gap-0.5" title="LLM evaluates this to YES or NO">
              <HelpCircle className="w-3 h-3" /> Returns YES / NO
            </span>
          </div>
          <textarea
            rows={4}
            value={data.prompt || ''}
            onChange={(e) => onUpdateNode(selectedNode.id, { prompt: e.target.value })}
            placeholder="e.g. Is this a request for technical support?"
            className="w-full px-3 py-2 rounded-lg bg-gray-950 border border-gray-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white placeholder-gray-500 outline-none transition resize-none leading-relaxed"
          />
          <p className="text-[10px] text-gray-500 mt-1">
            During execution, Inngest sends this question + user context to the LLM to choose the outgoing path.
          </p>
        </div>

        {/* Branch Guide */}
        <div className="p-3 rounded-lg bg-gray-950/80 border border-gray-800/80 space-y-2">
          <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider block">Branching Paths</span>
          <div className="flex items-center gap-2 text-emerald-400 text-[11px]">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>Connect <strong>YES</strong> handle to next step if True</span>
          </div>
          <div className="flex items-center gap-2 text-amber-400 text-[11px]">
            <XCircle className="w-3.5 h-3.5" />
            <span>Connect <strong>NO</strong> handle to next step if False</span>
          </div>
        </div>
      </div>

      {/* Inspector Footer (Actions) */}
      <div className="p-3 border-t border-gray-800 bg-gray-950/60">
        <button
          onClick={() => onDeleteNode(selectedNode.id)}
          className="w-full flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-rose-950/50 hover:bg-rose-900/60 border border-rose-800/60 text-rose-300 text-xs font-semibold transition"
        >
          <Trash2 className="w-3.5 h-3.5" /> Delete Node
        </button>
      </div>
    </aside>
  )
}
