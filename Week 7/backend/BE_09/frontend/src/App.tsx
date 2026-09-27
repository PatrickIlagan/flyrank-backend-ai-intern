import { useState, useEffect, useCallback } from 'react'
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  BackgroundVariant,
  type Connection,
  type Edge,
  type Node
} from '@xyflow/react'
import { Sparkles, Play, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react'

const initialNodes: Node[] = [
  {
    id: 'node-1',
    position: { x: 280, y: 80 },
    data: { label: 'Node 1: Support Triage' },
    style: {
      background: '#1f2937',
      color: '#f9fafb',
      border: '1px solid #374151',
      borderRadius: '8px',
      padding: '12px 18px',
      fontWeight: 500
    }
  },
  {
    id: 'node-2',
    position: { x: 120, y: 220 },
    data: { label: 'Node 2: Urgency Check' },
    style: {
      background: '#1f2937',
      color: '#f9fafb',
      border: '1px solid #374151',
      borderRadius: '8px',
      padding: '12px 18px',
      fontWeight: 500
    }
  },
  {
    id: 'node-3',
    position: { x: 440, y: 220 },
    data: { label: 'Node 3: Sales Classifier' },
    style: {
      background: '#1f2937',
      color: '#f9fafb',
      border: '1px solid #374151',
      borderRadius: '8px',
      padding: '12px 18px',
      fontWeight: 500
    }
  }
]

const initialEdges: Edge[] = [
  { id: 'e1-2', source: 'node-1', target: 'node-2', label: 'YES', animated: true, style: { stroke: '#10b981', strokeWidth: 2 } },
  { id: 'e1-3', source: 'node-1', target: 'node-3', label: 'NO', animated: true, style: { stroke: '#f59e0b', strokeWidth: 2 } }
]

export default function App() {
  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [backendHealth, setBackendHealth] = useState<'checking' | 'online' | 'offline'>('checking')

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const checkHealth = useCallback(() => {
    fetch('http://localhost:8000/health')
      .then((res) => res.json())
      .then((data) => {
        if (data.status === 'ok') {
          setBackendHealth('online')
        } else {
          setBackendHealth('offline')
        }
      })
      .catch(() => setBackendHealth('offline'))
  }, [])

  useEffect(() => {
    checkHealth()
    const timer = setInterval(checkHealth, 3000)
    return () => clearInterval(timer)
  }, [checkHealth])

  return (
    <div className="w-screen h-screen flex flex-col bg-[#090d16] text-gray-100">
      {/* Top Navbar */}
      <header className="h-14 border-b border-gray-800 bg-[#0f172a] px-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-500/20">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-sm font-semibold tracking-wide text-white">Visual AI Workflow System</h1>
            <p className="text-xs text-gray-400">FastAPI + Inngest + React Flow</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div 
            onClick={checkHealth}
            title="Click to recheck backend connection"
            className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-full bg-gray-900 hover:bg-gray-800 border border-gray-800 cursor-pointer transition select-none"
          >
            <span className="text-gray-400">Backend:</span>
            {backendHealth === 'online' ? (
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" /> Online (Port 8000)
              </span>
            ) : backendHealth === 'checking' ? (
              <span className="flex items-center gap-1 text-amber-400 font-medium">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Checking...
              </span>
            ) : (
              <span className="flex items-center gap-1 text-rose-400 font-medium">
                <AlertCircle className="w-3.5 h-3.5" /> Offline
              </span>
            )}
          </div>

          <div className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-full bg-indigo-950/60 border border-indigo-800/60 text-indigo-300">
            <span>Inngest Dev Server:</span>
            <span className="font-semibold">Port 8288</span>
          </div>

          <button
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white shadow-sm transition"
            onClick={() => alert('Phase 2 interactive editor & Phase 3 execution will connect here!')}
          >
            <Play className="w-3.5 h-3.5 fill-current" /> Run Workflow
          </button>
        </div>
      </header>

      {/* Main React Flow Canvas */}
      <main className="flex-1 w-full h-full relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          colorMode="dark"
        >
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="#1f2937" />
          <Controls className="bg-gray-900 border border-gray-800 fill-gray-300" />
          <MiniMap
            className="bg-gray-900/90 border border-gray-800 rounded-lg overflow-hidden"
            nodeColor="#374151"
            maskColor="rgba(0, 0, 0, 0.6)"
          />
        </ReactFlow>
      </main>
    </div>
  )
}
