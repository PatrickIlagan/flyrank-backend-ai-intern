import { useState } from 'react'
import { Play, Loader2, Terminal, CheckCircle2, XCircle, RotateCcw, ChevronDown, ChevronUp } from 'lucide-react'
import type { WorkflowRun } from '../types'

interface ExecutionPanelProps {
  isRunning: boolean
  currentRun: WorkflowRun | null
  onExecute: (context: string) => void
  onResetStatus: () => void
}

const PRESETS = [
  {
    label: '🚨 Outage',
    text: 'Our production database crashed and all checkout transactions are failing with 500 errors!'
  },
  {
    label: '💼 Enterprise Sales',
    text: 'We are a 200-person enterprise interested in custom licensing, security review, and annual pricing.'
  },
  {
    label: '❓ General Inquiry',
    text: 'What is your office headquarters address and customer support operating hours?'
  }
]

export function ExecutionPanel({
  isRunning,
  currentRun,
  onExecute,
  onResetStatus
}: ExecutionPanelProps) {
  const [context, setContext] = useState(PRESETS[0].text)
  const [isExpanded, setIsExpanded] = useState(true)

  const handleRun = () => {
    if (!context.trim() || isRunning) return
    onExecute(context.trim())
  }

  return (
    <div className="absolute bottom-4 left-6 right-6 max-w-4xl mx-auto z-20 transition-all duration-200">
      <div className="bg-gray-900/95 border border-gray-800 rounded-2xl shadow-2xl backdrop-blur-md overflow-hidden flex flex-col">
        {/* Panel Header */}
        <div className="px-5 py-3 border-b border-gray-800/80 bg-gray-950/60 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded-lg bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
              <Terminal className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className="text-xs font-bold text-white tracking-wide flex items-center gap-2">
                Inngest Workflow Execution Controller
                {isRunning && (
                  <span className="flex items-center gap-1 text-[10px] font-medium text-blue-400 bg-blue-950/80 px-2 py-0.5 rounded-full border border-blue-800/60 animate-pulse">
                    <Loader2 className="w-2.5 h-2.5 animate-spin" /> Inngest Step Running...
                  </span>
                )}
                {currentRun?.status === 'completed' && (
                  <span className="flex items-center gap-1 text-[10px] font-medium text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded-full border border-emerald-800/60">
                    <CheckCircle2 className="w-2.5 h-2.5" /> Run Completed ({currentRun.steps.length} Steps)
                  </span>
                )}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {currentRun && (
              <button
                onClick={onResetStatus}
                title="Reset node highlight colors back to idle"
                className="flex items-center gap-1 text-[11px] px-2.5 py-1 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition"
              >
                <RotateCcw className="w-3 h-3" /> Reset State
              </button>
            )}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="w-6 h-6 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white flex items-center justify-center transition"
            >
              {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Panel Body */}
        {isExpanded && (
          <div className="p-4 space-y-3.5 text-xs">
            {/* Input Context & Trigger */}
            <div className="flex flex-col sm:flex-row gap-2.5">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  disabled={isRunning}
                  placeholder="Enter user message or context for the AI workflow to evaluate..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-950 border border-gray-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white placeholder-gray-500 outline-none transition disabled:opacity-50"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleRun()
                  }}
                />
              </div>

              <button
                onClick={handleRun}
                disabled={isRunning || !context.trim()}
                className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-800 disabled:text-gray-500 font-semibold text-white flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 transition shrink-0"
              >
                {isRunning ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Orchestrating...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-current" /> Execute via Inngest
                  </>
                )}
              </button>
            </div>

            {/* Quick Presets */}
            <div className="flex items-center gap-2 overflow-x-auto pb-0.5">
              <span className="text-[11px] text-gray-500 shrink-0 font-medium">Quick Presets:</span>
              {PRESETS.map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => setContext(preset.text)}
                  disabled={isRunning}
                  className="px-2.5 py-1 rounded-lg bg-gray-950 hover:bg-gray-800 border border-gray-800/80 text-[11px] text-gray-300 hover:text-white transition shrink-0"
                >
                  {preset.label}
                </button>
              ))}
            </div>

            {/* Live Step Logs */}
            {currentRun && currentRun.steps.length > 0 && (
              <div className="mt-2 border-t border-gray-800/60 pt-3">
                <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider block mb-2">
                  Step Traversal History (Run ID: {currentRun.id})
                </span>
                <div className="max-h-36 overflow-y-auto space-y-1.5 pr-1">
                  {currentRun.steps.map((step, index) => (
                    <div
                      key={index}
                      className="p-2 rounded-lg bg-gray-950/80 border border-gray-800/60 flex items-start justify-between gap-3 text-[11px]"
                    >
                      <div className="flex items-start gap-2 overflow-hidden">
                        <span className="w-4 h-4 rounded-full bg-gray-800 text-[10px] font-bold text-gray-300 flex items-center justify-center shrink-0 mt-0.5">
                          {index + 1}
                        </span>
                        <div>
                          <div className="font-semibold text-gray-200">
                            {step.node_title}
                          </div>
                          <div className="text-gray-400 text-[10px] mt-0.5 line-clamp-1">
                            Q: {step.prompt}
                          </div>
                          <div className="text-indigo-400/90 text-[10px] mt-0.5">
                            {step.reason}
                          </div>
                        </div>
                      </div>

                      <div className="shrink-0">
                        {step.decision === 'YES' ? (
                          <span className="flex items-center gap-1 font-bold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/50">
                            <CheckCircle2 className="w-3 h-3" /> YES
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 font-bold text-amber-400 bg-amber-950/80 px-2 py-0.5 rounded border border-amber-800/50">
                            <XCircle className="w-3 h-3" /> NO
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
