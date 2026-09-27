import { useRef } from 'react'
import { Plus, RotateCcw, Trash, Save, Download, Upload } from 'lucide-react'

interface ToolbarProps {
  onAddNode: () => void
  onResetTemplate: () => void
  onClearGraph: () => void
  onExportGraph: () => void
  onImportGraph: (e: React.ChangeEvent<HTMLInputElement>) => void
  nodeCount: number
  edgeCount: number
}

export function Toolbar({
  onAddNode,
  onResetTemplate,
  onClearGraph,
  onExportGraph,
  onImportGraph,
  nodeCount,
  edgeCount
}: ToolbarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  return (
    <div className="absolute left-6 top-18 z-10 flex items-center gap-2 bg-gray-900/90 border border-gray-800 p-1.5 rounded-xl shadow-xl backdrop-blur-md text-xs">
      {/* Add Node Button */}
      <button
        onClick={onAddNode}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-sm transition"
      >
        <Plus className="w-3.5 h-3.5" /> Add Decision Node
      </button>

      <div className="h-5 w-px bg-gray-800 mx-1" />

      {/* Export JSON */}
      <button
        onClick={onExportGraph}
        title="Export workflow graph as JSON file"
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg hover:bg-gray-800 text-gray-300 hover:text-white transition"
      >
        <Download className="w-3.5 h-3.5 text-gray-400" /> Export
      </button>

      {/* Import JSON */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        onChange={onImportGraph}
        className="hidden"
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        title="Import workflow graph from JSON file"
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg hover:bg-gray-800 text-gray-300 hover:text-white transition"
      >
        <Upload className="w-3.5 h-3.5 text-gray-400" /> Import
      </button>

      <div className="h-5 w-px bg-gray-800 mx-1" />

      {/* Reset Template */}
      <button
        onClick={onResetTemplate}
        title="Reset graph to default starter template"
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg hover:bg-gray-800 text-gray-300 hover:text-white transition"
      >
        <RotateCcw className="w-3.5 h-3.5 text-gray-400" /> Reset
      </button>

      {/* Clear Graph */}
      <button
        onClick={onClearGraph}
        title="Clear all nodes and edges"
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg hover:bg-rose-950/40 text-gray-400 hover:text-rose-400 transition"
      >
        <Trash className="w-3.5 h-3.5" /> Clear
      </button>

      <div className="h-5 w-px bg-gray-800 mx-1" />

      {/* Graph Stats Badge */}
      <div className="flex items-center gap-2 px-2 text-[11px] text-gray-400 select-none">
        <span>{nodeCount} nodes</span>
        <span>•</span>
        <span>{edgeCount} edges</span>
        <span>•</span>
        <span className="flex items-center gap-1 text-emerald-400/90 text-[10px]" title="Changes persist across reloads">
          <Save className="w-3 h-3" /> Auto-saved
        </span>
      </div>
    </div>
  )
}
