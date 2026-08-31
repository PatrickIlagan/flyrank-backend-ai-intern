import sqlite3
from fastapi import FastAPI
from fastapi.responses import JSONResponse

DB_NAME = "tasks.db"

app = FastAPI(
    title="Task API (SQLite)",
    version="2.0",
    description="A persistent Task Management CRUD API backed by SQLite."
)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Buy groceries", 0))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Read Week 3 Documentation", 1))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Connect CRUD to SQLite", 0))
        conn.commit()
        
    conn.close()

init_db()


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


@app.get("/tasks", summary="List All Tasks", tags=["Tasks"])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    
    return [{"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows]