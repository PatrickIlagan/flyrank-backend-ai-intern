import sqlite3
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

DB_NAME = "tasks.db"

app = FastAPI(
    title="Task API (SQLite)",
    version="2.0",
    description="A persistent Task Management CRUD API backed by SQLite."
)

# Helper function to get a database connection with dictionary-like row access
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database table and seed starter data only if empty
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Create tasks table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    # 2. Count existing rows to prevent duplicate seeding
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    # 3. Seed starter data only when table is completely empty
    if count == 0:
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Buy groceries", 0))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Read Week 3 Documentation", 1))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Connect CRUD to SQLite", 0))
        conn.commit()
        
    conn.close()

# Run database setup on startup
init_db()


# 1. Root and Health Endpoints
@app.get("/", summary="API Root Descriptor", tags=["General"])
def read_root():
    return {
        "name": "Task API (SQLite)",
        "version": "2.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "ok"}


# 2. Read Endpoints (Reads directly from SQLite tasks.db)
@app.get("/tasks", summary="List All Tasks", tags=["Tasks"])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    
    # Convert SQLite rows into clean JSON list
    return [{"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows]

@app.get("/tasks/{task_id}", summary="Get Task by ID", tags=["Tasks"])
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Use parameterized query to find the specific row safely
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    # If no task with that ID exists in SQLite, return 404
    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )
        
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

# 3. Create a new task (POST /tasks)
@app.post("/tasks", summary="Create a new task", tags=["Tasks"])
async def create_task(request: Request):
    # Parse incoming JSON body
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid or missing JSON body"}
        )

    # Validate title
    title = body.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"}
        )

    # Insert into SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (title.strip(), 0)
    )
    conn.commit()
    
    new_id = cursor.lastrowid
    conn.close()

    new_task = {
        "id": new_id,
        "title": title.strip(),
        "done": False
    }

    return JSONResponse(
        status_code=201,
        content=new_task
    )

# 4. Update a task (PUT /tasks/{task_id})
@app.put("/tasks/{task_id}", summary="Update a task", tags=["Tasks"])
async def update_task(task_id: int, request: Request):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the task exists
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )

    # Parse incoming JSON
    try:
        body = await request.json()
    except Exception:
        conn.close()
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid or missing JSON body"}
        )

    if not isinstance(body, dict) or not body:
        conn.close()
        return JSONResponse(
            status_code=400,
            content={"error": "Request body cannot be empty"}
        )

    current_title = row["title"]
    current_done = row["done"]

    # Validate title if provided
    if "title" in body:
        title_val = body["title"]
        if not isinstance(title_val, str) or not title_val.strip():
            conn.close()
            return JSONResponse(
                status_code=400,
                content={"error": "Title must be a non-empty string"}
            )
        current_title = title_val.strip()

    # Validate done if provided
    if "done" in body:
        done_val = body["done"]
        if not isinstance(done_val, bool):
            conn.close()
            return JSONResponse(
                status_code=400,
                content={"error": "Done must be a boolean (true or false)"}
            )
        current_done = 1 if done_val else 0

    # Execute SQL UPDATE query
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (current_title, current_done, task_id)
    )
    conn.commit()
    conn.close()

    return {
        "id": task_id,
        "title": current_title,
        "done": bool(current_done)
    }


# 5. Delete a task (DELETE /tasks/{task_id})
@app.delete("/tasks/{task_id}", summary="Delete a task", tags=["Tasks"])
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the task exists
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )

    # Execute SQL DELETE query
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return Response(status_code=204)