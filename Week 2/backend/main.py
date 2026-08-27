from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI(title="Task API", version="1.0")

tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read Week 2 Documentation", "done": True},
    {"id": 3, "title": "Build my own portfolio", "done": False},
]


# 1. Root Endpoints:
@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

#2. Read endpoints with 404
@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )

#3. Create a new task (POST /tasks)
@app.post("/tasks")
async def create_task(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid or missing JSON body"}
        )

    title = body.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"}
        )

    next_id = max([t["id"] for t in tasks], default=0) + 1
    new_task = {
        "id": next_id,
        "title": title.strip(),
        "done": False
    }

    tasks.append(new_task)

    return JSONResponse(
        status_code=201,
        content=new_task
    )

# 4. Update a task
@app.put("/tasks/{task_id}")
async def update_task(task_id: int, request: Request):
    target_task = None
    for task in tasks:
        if task["id"] == task_id:
            target_task = task
            break

    if not target_task:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid or missing JSON body"}
        )

    if not isinstance(body, dict) or not body:
        return JSONResponse(
            status_code=400,
            content={"error": "Request body cannot be empty"}
        )

    if "title" in body:
        title = body["title"]
        if not isinstance(title, str) or not title.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Title must be a non-empty string"}
            )
        target_task["title"] = title.strip()

    if "done" in body:
        done = body["done"]
        if not isinstance(done, bool):
            return JSONResponse(
                status_code=400,
                content={"error": "Done must be a boolean (true or false)"}
            )
        target_task["done"] = done
    return target_task

#4. Deleting a task (DELETE /tasks/{task_id})]
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    # Find the task
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            # Return 204 No Content with an empty body
            return Response(status_code=204)
    # If not found, return 404
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )