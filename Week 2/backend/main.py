from fastapi import FastAPI, Request
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