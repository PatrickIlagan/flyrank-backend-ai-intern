import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dev@localhost:5432/tasks")

app = FastAPI(
    title="Task API (PostgreSQL + Docker)",
    version="3.0",
    description="A persistent Task Management CRUD API backed by PostgreSQL running in Docker."
)

import time

# Helper function to get a PostgreSQL database connection
def get_db_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

# Initialize database table and seed starter data only if empty
def init_db():
    for attempt in range(10):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 1. Create tasks table if it does not exist
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS tasks (
                            id SERIAL PRIMARY KEY,
                            title TEXT NOT NULL,
                            done BOOLEAN NOT NULL DEFAULT FALSE
                        );
                    """)
                    
                    # 2. Count existing rows
                    cursor.execute("SELECT COUNT(*) FROM tasks;")
                    row = cursor.fetchone()
                    count = row["count"] if row else 0
                    
                    # 3. Seed starter data only when table is completely empty
                    if count == 0:
                        cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s);", ("Buy groceries", False))
                        cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s);", ("Read Week 3 Documentation", True))
                        cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s);", ("Containerize CRUD with Docker", False))
                        conn.commit()
            print("Database initialized successfully!")
            break
        except Exception as e:
            print(f"Waiting for database connection (attempt {attempt + 1}/10)...")
            time.sleep(1)

# Run database setup on startup
init_db()


# 1. Root and Health Endpoints
@app.get("/", summary="API Root Descriptor", tags=["General"])
def read_root():
    return {
        "name": "Task API (PostgreSQL + Docker)",
        "version": "3.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "ok"}


# 1. Read all tasks (GET /tasks)
@app.get("/tasks", summary="List All Tasks", tags=["Tasks"])
def get_tasks():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks ORDER BY id ASC;")
            rows = cursor.fetchall()
            return [{"id": row["id"], "title": row["title"], "done": row["done"]} for row in rows]

# 2. Read single task by ID (GET /tasks/{task_id})
@app.get("/tasks/{task_id}", summary="Get Task by ID", tags=["Tasks"])
def get_task(task_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Use %s placeholder to query PostgreSQL safely
            cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s;", (task_id,))
            row = cursor.fetchone()
            
            # If task doesn't exist, return 404
            if row is None:
                return JSONResponse(
                    status_code=404,
                    content={"error": f"Task {task_id} not found"}
                )
                
            return {"id": row["id"], "title": row["title"], "done": row["done"]}

# 3. Create a task (POST /tasks)
@app.post("/tasks", summary="Create a new task", tags=["Tasks"])
async def create_task(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid or missing JSON body"})

    title = body.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is required and cannot be empty"})

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Use RETURNING to get the generated ID and row in one step
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done;",
                (title.strip(), False)
            )
            new_task = cursor.fetchone()
            conn.commit()

            return JSONResponse(
                status_code=201,
                content={"id": new_task["id"], "title": new_task["title"], "done": new_task["done"]}
            )


# 4. Update a task (PUT /tasks/{task_id})
@app.put("/tasks/{task_id}", summary="Update a task", tags=["Tasks"])
async def update_task(task_id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid or missing JSON body"})

    if not isinstance(body, dict) or not body:
        return JSONResponse(status_code=400, content={"error": "Request body cannot be empty"})

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Check if task exists
            cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s;", (task_id,))
            current = cursor.fetchone()
            if current is None:
                return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})

            current_title = current["title"]
            current_done = current["done"]

            if "title" in body:
                title_val = body["title"]
                if not isinstance(title_val, str) or not title_val.strip():
                    return JSONResponse(status_code=400, content={"error": "Title must be a non-empty string"})
                current_title = title_val.strip()

            if "done" in body:
                done_val = body["done"]
                if not isinstance(done_val, bool):
                    return JSONResponse(status_code=400, content={"error": "Done must be a boolean"})
                current_done = done_val

            # Execute UPDATE with RETURNING
            cursor.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done;",
                (current_title, current_done, task_id)
            )
            updated = cursor.fetchone()
            conn.commit()

            return {"id": updated["id"], "title": updated["title"], "done": updated["done"]}


# 5. Delete a task (DELETE /tasks/{task_id})
@app.delete("/tasks/{task_id}", summary="Delete a task", tags=["Tasks"])
def delete_task(task_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s RETURNING id;", (task_id,))
            deleted = cursor.fetchone()
            if deleted is None:
                return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
                
            conn.commit()
            return Response(status_code=204)