import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
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
import { DecisionNode } from './components/DecisionNode'
import { WorkflowEdge } from './components/WorkflowEdge'
import { NodeInspector } from './components/NodeInspector'
import { Toolbar } from './components/Toolbar'
import { ExecutionPanel } from './components/ExecutionPanel'
import type { DecisionNodeData, WorkflowRun } from './types'

const LOCAL_STORAGE_KEY = 'visual_ai_workflow_graph_v1'

const DEFAULT_NODES: Node<DecisionNodeData>[] = [
  {
    id: 'node-1',
    type: 'decisionNode',
    position: { x: 300, y: 80 },
    data: {
      title: 'Support Triage',
      prompt: 'Is this a technical support request or bug report?',
      status: 'idle'
    }
  },
  {
    id: 'node-2',
    type: 'decisionNode',
    position: { x: 100, y: 300 },
    data: {
      title: 'Urgency Check',
      prompt: 'Is this an urgent production outage affecting critical services?',
      status: 'idle'
    }
  },
  {
    id: 'node-3',
    type: 'decisionNode',
    position: { x: 500, y: 300 },
    data: {
      title: 'Sales Classifier',
      prompt: 'Is this a commercial sales, enterprise, or pricing inquiry?',
      status: 'idle'
    }
  },
  {
    id: 'node-4',
    type: 'decisionNode',
    position: { x: 0, y: 520 },
    data: {
      title: 'On-Call Escalation',
      prompt: 'Should this trigger an immediate SMS alert to on-call engineering?',
      status: 'idle'
    }
  },
  {
    id: 'node-5',
    type: 'decisionNode',
    position: { x: 220, y: 520 },
    data: {
      title: 'Standard Support',
      prompt: 'Should this be routed to the standard Tier-1 support queue?',
      status: 'idle'
    }
  }
]

const DEFAULT_EDGES: Edge[] = [
  {
    id: 'e1-2',
    source: 'node-1',
    target: 'node-2',
    sourceHandle: 'yes',
    type: 'workflowEdge',
    data: { label: 'YES' }
  },
  {
    id: 'e1-3',
    source: 'node-1',
    target: 'node-3',
    sourceHandle: 'no',
    type: 'workflowEdge',
    data: { label: 'NO' }
  },
  {
    id: 'e2-4',
    source: 'node-2',
    target: 'node-4',
    sourceHandle: 'yes',
    type: 'workflowEdge',
    data: { label: 'YES' }
  },
  {
    id: 'e2-5',
    source: 'node-2',
    target: 'node-5',
    sourceHandle: 'no',
    type: 'workflowEdge',
    data: { label: 'NO' }
  }
]

export default function App() {
  // Load initial graph from LocalStorage if available
  const [initialGraph] = useState(() => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved)
        if (Array.isArray(parsed.nodes) && Array.isArray(parsed.edges)) {
          return { nodes: parsed.nodes, edges: parsed.edges }
        }
      }
    } catch (e) {
      console.warn('Failed to parse saved graph from LocalStorage:', e)
    }
    return { nodes: DEFAULT_NODES, edges: DEFAULT_EDGES }
  })

  const [nodes, setNodes, onNodesChange] = useNodesState<Node<DecisionNodeData>>(initialGraph.nodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialGraph.edges)
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  const [backendHealth, setBackendHealth] = useState<'checking' | 'online' | 'offline'>('checking')

  // Execution & Live Polling State
  const [isRunning, setIsRunning] = useState(false)
  const [currentRun, setCurrentRun] = useState<WorkflowRun | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Register custom node and edge types
  const nodeTypes = useMemo(() => ({ decisionNode: DecisionNode }), [])
  const edgeTypes = useMemo(() => ({ workflowEdge: WorkflowEdge }), [])

  // Auto-save graph to LocalStorage whenever modified
  useEffect(() => {
    try {
      localStorage.setItem(
        LOCAL_STORAGE_KEY,
        JSON.stringify({ nodes, edges })
      )
    } catch (e) {
      console.error('Failed to save graph to LocalStorage:', e)
    }
  }, [nodes, edges])

  // Clear polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current)
    }
  }, [])

  // Periodic Backend Health Check
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

  // Connection Handler: Auto-assigns YES or NO edge styling based on source handle
  const onConnect = useCallback(
    (params: Connection) => {
      const isYes = params.sourceHandle === 'yes'
      const newEdge: Edge = {
        ...params,
        id: `edge-${params.source}-${params.sourceHandle}-${params.target}-${Date.now()}`,
        type: 'workflowEdge',
        sourceHandle: params.sourceHandle,
        data: { label: isYes ? 'YES' : 'NO' }
      }
      setEdges((eds) => addEdge(newEdge, eds))
    },
    [setEdges]
  )

  // Node Selection
  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNodeId(node.id)
  }, [])

  const onPaneClick = useCallback(() => {
    setSelectedNodeId(null)
  }, [])

  // Node Editing
  const handleUpdateNode = useCallback(
    (nodeId: string, updates: Partial<DecisionNodeData>) => {
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id === nodeId) {
            return {
              ...node,
              data: {
                ...node.data,
                ...updates
              }
            }
          }
          return node
        })
      )
    },
    [setNodes]
  )

  // Node Deletion
  const handleDeleteNode = useCallback(
    (nodeId: string) => {
      setNodes((nds) => nds.filter((node) => node.id !== nodeId))
      setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId))
      if (selectedNodeId === nodeId) {
        setSelectedNodeId(null)
      }
    },
    [setNodes, setEdges, selectedNodeId]
  )

  // Add Node
  const handleAddNode = useCallback(() => {
    const newId = `node-${Date.now().toString().slice(-4)}`
    const newNode: Node<DecisionNodeData> = {
      id: newId,
      type: 'decisionNode',
      position: {
        x: 250 + Math.random() * 100 - 50,
        y: 200 + Math.random() * 100 - 50
      },
      data: {
        title: `Decision Step ${nodes.length + 1}`,
        prompt: 'Does this meet the decision criteria?',
        status: 'idle'
      }
    }
    setNodes((nds) => [...nds, newNode])
    setSelectedNodeId(newId)
  }, [nodes.length, setNodes])

  // Reset Template
  const handleResetTemplate = useCallback(() => {
    if (confirm('Reset graph to default starter template? Unsaved changes will be replaced.')) {
      setNodes(DEFAULT_NODES)
      setEdges(DEFAULT_EDGES)
      setSelectedNodeId(null)
      handleResetStatus()
    }
  }, [setNodes, setEdges])

  // Clear Graph
  const handleClearGraph = useCallback(() => {
    if (confirm('Clear all nodes and connections from the canvas?')) {
      setNodes([])
      setEdges([])
      setSelectedNodeId(null)
      handleResetStatus()
    }
  }, [setNodes, setEdges])

  // Export Graph as JSON
  const handleExportGraph = useCallback(() => {
    const exportData = {
      version: '1.0',
      exportedAt: new Date().toISOString(),
      nodes,
      edges
    }
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ai-workflow-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }, [nodes, edges])

  // Import Graph from JSON
  const handleImportGraph = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (!file) return

      const reader = new FileReader()
      reader.onload = (event) => {
        try {
          const content = event.target?.result as string
          const parsed = JSON.parse(content)
          if (Array.isArray(parsed.nodes) && Array.isArray(parsed.edges)) {
            setNodes(parsed.nodes)
            setEdges(parsed.edges)
            setSelectedNodeId(null)
            handleResetStatus()
          } else {
            alert('Invalid workflow JSON file format.')
          }
        } catch (err) {
          alert('Failed to parse JSON file.')
        }
      }
      reader.readAsText(file)
      e.target.value = ''
    },
    [setNodes, setEdges]
  )

  // Reset Execution Highlighting State
  const handleResetStatus = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
    setIsRunning(false)
    setCurrentRun(null)
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        data: {
          ...n.data,
          status: 'idle',
          lastReason: undefined
        }
      }))
    )
    setEdges((eds) =>
      eds.map((e) => ({
        ...e,
        animated: false,
        data: {
          ...e.data,
          isActive: false
        }
      }))
    )
  }, [setNodes, setEdges])

  // Execute Workflow via Inngest and Poll Run Status
  const handleExecute = useCallback(
    async (contextText: string) => {
      if (isRunning) return
      setIsRunning(true)

      // Reset node status to idle first
      setNodes((nds) =>
        nds.map((n) => ({
          ...n,
          data: {
            ...n.data,
            status: 'idle',
            lastReason: undefined
          }
        }))
      )
      setEdges((eds) =>
        eds.map((e) => ({
          ...e,
          animated: false,
          data: {
            ...e.data,
            isActive: false
          }
        }))
      )

      try {
        const response = await fetch('http://localhost:8000/api/workflow/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            context: contextText,
            nodes,
            edges
          })
        })

        if (!response.ok) {
          throw new Error(`Execution request failed with status: ${response.status}`)
        }

        const data = await response.json()
        const runId = data.run_id

        if (pollingRef.current) clearInterval(pollingRef.current)

        const pollStatus = async () => {
          try {
            const res = await fetch(`http://localhost:8000/api/workflow/runs/${runId}`)
            if (!res.ok) return
            const runData: WorkflowRun = await res.json()
            setCurrentRun(runData)

            // Update nodes status based on completed steps & active node
            const completedMap = new Map<string, { decision: 'YES' | 'NO'; reason: string }>()
            runData.steps.forEach((step) => {
              completedMap.set(step.node_id, {
                decision: step.decision,
                reason: step.reason
              })
            })

            setNodes((nds) =>
              nds.map((node) => {
                if (completedMap.has(node.id)) {
                  const stepInfo = completedMap.get(node.id)!
                  return {
                    ...node,
                    data: {
                      ...node.data,
                      status: stepInfo.decision === 'YES' ? 'completed_yes' : 'completed_no',
                      lastReason: stepInfo.reason
                    }
                  }
                }
                if (runData.status === 'running' && runData.active_node_id === node.id) {
                  return {
                    ...node,
                    data: {
                      ...node.data,
                      status: 'running'
                    }
                  }
                }
                return node
              })
            )

            // Update edges active status
            setEdges((eds) =>
              eds.map((edge) => {
                const isActive = edge.id === runData.active_edge_id
                return {
                  ...edge,
                  animated: isActive,
                  data: {
                    ...edge.data,
                    isActive
                  }
                }
              })
            )

            // Stop polling when run finishes
            if (runData.status === 'completed' || runData.status === 'failed') {
              if (pollingRef.current) {
                clearInterval(pollingRef.current)
                pollingRef.current = null
              }
              setIsRunning(false)
            }
          } catch (err) {
            console.error('Error polling run status:', err)
          }
        }

        await pollStatus()
        pollingRef.current = setInterval(pollStatus, 500)
      } catch (err) {
        console.error('Failed to trigger workflow execution:', err)
        setIsRunning(false)
        alert('Failed to start workflow execution. Is the FastAPI backend running on port 8000?')
      }
    },
    [isRunning, nodes, edges, setNodes, setEdges]
  )

  // Currently Selected Node Object
  const selectedNode = useMemo(
    () => nodes.find((n) => n.id === selectedNodeId) || null,
    [nodes, selectedNodeId]
  )

  return (
    <div className="w-screen h-screen flex flex-col bg-[#090d16] text-gray-100 select-none">
      {/* Top Navbar */}
      <header className="h-14 border-b border-gray-800 bg-[#0f172a] px-6 flex items-center justify-between z-10 shrink-0">
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
            className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-full bg-gray-900 hover:bg-gray-800 border border-gray-800 cursor-pointer transition"
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
            disabled={isRunning}
            onClick={() => handleExecute('Our production database crashed and all checkout transactions are failing!')}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-800 disabled:text-gray-500 text-xs font-semibold text-white shadow-sm transition"
          >
            <Play className="w-3.5 h-3.5 fill-current" /> {isRunning ? 'Running...' : 'Quick Run'}
          </button>
        </div>
      </header>

      {/* Main Canvas Area */}
      <main className="flex-1 w-full h-full relative overflow-hidden">
        {/* Graph Toolbar */}
        <Toolbar
          onAddNode={handleAddNode}
          onResetTemplate={handleResetTemplate}
          onClearGraph={handleClearGraph}
          onExportGraph={handleExportGraph}
          onImportGraph={handleImportGraph}
          nodeCount={nodes.length}
          edgeCount={edges.length}
        />

        {/* Node Inspector Drawer */}
        <NodeInspector
          selectedNode={selectedNode}
          onUpdateNode={handleUpdateNode}
          onDeleteNode={handleDeleteNode}
          onClose={() => setSelectedNodeId(null)}
        />

        {/* React Flow Canvas */}
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
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

        {/* Execution Controller & Logs Panel */}
        <ExecutionPanel
          isRunning={isRunning}
          currentRun={currentRun}
          onExecute={handleExecute}
          onResetStatus={handleResetStatus}
        />
      </main>
    </div>
  )
}

