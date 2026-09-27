import datetime
from typing import Dict, Any, List, Optional
import inngest
from inngest_client import inngest_client
from llm import evaluate_decision

# In-memory execution store for tracking runs and live visualization
runs: Dict[str, Dict[str, Any]] = {}

DEFAULT_WORKFLOW = {
    "nodes": [
        {
            "id": "node-1",
            "type": "decisionNode",
            "position": {"x": 250, "y": 50},
            "data": {
                "title": "Support Triage",
                "prompt": "Is this a technical support request or bug report?"
            }
        },
        {
            "id": "node-2",
            "type": "decisionNode",
            "position": {"x": 80, "y": 250},
            "data": {
                "title": "Urgency Check",
                "prompt": "Is this an urgent production outage affecting critical services?"
            }
        },
        {
            "id": "node-3",
            "type": "decisionNode",
            "position": {"x": 450, "y": 250},
            "data": {
                "title": "Sales Classifier",
                "prompt": "Is this a commercial sales, enterprise, or pricing inquiry?"
            }
        },
        {
            "id": "node-4",
            "type": "decisionNode",
            "position": {"x": 0, "y": 450},
            "data": {
                "title": "On-Call Escalation",
                "prompt": "Should this trigger an immediate SMS alert to on-call engineering?"
            }
        },
        {
            "id": "node-5",
            "type": "decisionNode",
            "position": {"x": 200, "y": 450},
            "data": {
                "title": "Standard Support",
                "prompt": "Should this be logged into the standard Tier-1 support queue?"
            }
        }
    ],
    "edges": [
        {
            "id": "edge-1-2",
            "source": "node-1",
            "target": "node-2",
            "sourceHandle": "yes",
            "data": {"label": "YES"}
        },
        {
            "id": "edge-1-3",
            "source": "node-1",
            "target": "node-3",
            "sourceHandle": "no",
            "data": {"label": "NO"}
        },
        {
            "id": "edge-2-4",
            "source": "node-2",
            "target": "node-4",
            "sourceHandle": "yes",
            "data": {"label": "YES"}
        },
        {
            "id": "edge-2-5",
            "source": "node-2",
            "target": "node-5",
            "sourceHandle": "no",
            "data": {"label": "NO"}
        }
    ]
}

@inngest_client.create_function(
    fn_id="execute-workflow",
    trigger=inngest.TriggerEvent(event="workflow/execute")
)
async def execute_workflow(ctx: inngest.Context) -> dict:
    """
    Executes a visual AI workflow step-by-step:
    1. Traverses nodes beginning from start_node_id (or root).
    2. Runs an Inngest step per node, calling the LLM to evaluate YES or NO.
    3. Finds the matching outgoing edge ('yes' or 'no').
    4. Advances to the next node until no further edges exist.
    """
    data = ctx.event.data
    run_id = data.get("run_id")
    context = data.get("context", "")
    nodes = data.get("nodes", DEFAULT_WORKFLOW["nodes"])
    edges = data.get("edges", DEFAULT_WORKFLOW["edges"])
    start_node_id = data.get("start_node_id", nodes[0]["id"] if nodes else None)

    if not run_id:
        return {"error": "Missing run_id"}

    # Initialize run record in store if not present
    if run_id not in runs:
        runs[run_id] = {
            "id": run_id,
            "status": "running",
            "context": context,
            "active_node_id": start_node_id,
            "active_edge_id": None,
            "steps": [],
            "created_at": datetime.datetime.now().isoformat(),
            "completed_at": None
        }

    node_map = {n["id"]: n for n in nodes}
    current_node_id = start_node_id
    traversal_order = []

    while current_node_id and current_node_id in node_map:
        current_node = node_map[current_node_id]
        node_prompt = current_node.get("data", {}).get("prompt", "Is this valid?")
        node_title = current_node.get("data", {}).get("title", current_node_id)
        step_id = f"node-{current_node_id}"

        # Update live active node
        runs[run_id]["active_node_id"] = current_node_id
        runs[run_id]["status"] = "running"

        # Execute decision step durably through Inngest
        def run_step() -> dict:
            decision, reason = evaluate_decision(node_prompt, context)
            return {
                "node_id": current_node_id,
                "node_title": node_title,
                "prompt": node_prompt,
                "decision": decision,
                "reason": reason,
                "timestamp": datetime.datetime.now().isoformat()
            }

        step_result = await ctx.step.run(step_id, run_step)
        traversal_order.append(step_result)

        # Brief pacing so the client visualizer can highlight the decision
        await ctx.step.sleep(f"pace-{current_node_id}", datetime.timedelta(seconds=1))

        # Record steps in memory run store cleanly
        runs[run_id]["steps"] = list(traversal_order)

        decision = step_result["decision"].upper()
        handle_target = "yes" if decision == "YES" else "no"

        # Find matching outgoing edge
        matching_edge = None
        for edge in edges:
            if edge.get("source") == current_node_id:
                edge_handle = (edge.get("sourceHandle") or "").lower()
                edge_label = (edge.get("data", {}).get("label") or edge.get("label") or "").upper()
                if edge_handle == handle_target or edge_label == decision:
                    matching_edge = edge
                    break

        if matching_edge:
            runs[run_id]["active_edge_id"] = matching_edge.get("id")
            current_node_id = matching_edge.get("target")
        else:
            # End of branch reached
            runs[run_id]["active_edge_id"] = None
            current_node_id = None

    # Mark run completed
    runs[run_id]["status"] = "completed"
    runs[run_id]["active_node_id"] = None
    runs[run_id]["completed_at"] = datetime.datetime.now().isoformat()

    return {
        "run_id": run_id,
        "status": "completed",
        "steps_count": len(traversal_order),
        "steps": traversal_order
    }

async def run_workflow_direct(
    run_id: str,
    context: str,
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    start_node_id: Optional[str] = None
) -> dict:
    """
    Direct asynchronous execution fallback when Inngest dev server is not actively connected.
    Executes the exact same step-by-step logic and updates runs[run_id] with 1s pacing.
    """
    import asyncio

    if run_id not in runs:
        runs[run_id] = {
            "id": run_id,
            "status": "running",
            "context": context,
            "active_node_id": start_node_id,
            "active_edge_id": None,
            "steps": [],
            "created_at": datetime.datetime.now().isoformat(),
            "completed_at": None
        }

    node_map = {n["id"]: n for n in nodes}
    current_node_id = start_node_id or (nodes[0]["id"] if nodes else None)
    traversal_order = []

    while current_node_id and current_node_id in node_map:
        current_node = node_map[current_node_id]
        node_prompt = current_node.get("data", {}).get("prompt", "Is this valid?")
        node_title = current_node.get("data", {}).get("title", current_node_id)

        runs[run_id]["active_node_id"] = current_node_id
        runs[run_id]["status"] = "running"

        decision, reason = evaluate_decision(node_prompt, context)
        step_result = {
            "node_id": current_node_id,
            "node_title": node_title,
            "prompt": node_prompt,
            "decision": decision,
            "reason": reason,
            "timestamp": datetime.datetime.now().isoformat()
        }
        traversal_order.append(step_result)

        # 1-second visual pacing so client visualizer can observe state transitions
        await asyncio.sleep(1)

        runs[run_id]["steps"] = list(traversal_order)

        decision = step_result["decision"].upper()
        handle_target = "yes" if decision == "YES" else "no"

        matching_edge = None
        for edge in edges:
            if edge.get("source") == current_node_id:
                edge_handle = (edge.get("sourceHandle") or "").lower()
                edge_label = (edge.get("data", {}).get("label") or edge.get("label") or "").upper()
                if edge_handle == handle_target or edge_label == decision:
                    matching_edge = edge
                    break

        if matching_edge:
            runs[run_id]["active_edge_id"] = matching_edge.get("id")
            current_node_id = matching_edge.get("target")
        else:
            runs[run_id]["active_edge_id"] = None
            current_node_id = None

    runs[run_id]["status"] = "completed"
    runs[run_id]["active_node_id"] = None
    runs[run_id]["completed_at"] = datetime.datetime.now().isoformat()

    return {
        "run_id": run_id,
        "status": "completed",
        "steps_count": len(traversal_order),
        "steps": traversal_order
    }
