import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dev@localhost:5432/tasks")

app = FastAPI(
    title="Task API (PostgreSQL + Docker)",
    version="3.0",
    description="A persistent Task Management CRUD API backed by PostgreSQL running in Docker."
)

# Helper function to get a PostgreSQL database connection
def get_db_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

# Initialize database table and seed starter data only if empty
def init_db():
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
    except Exception as e:
        print(f"Database initialization warning: {e}")

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


# 2. Read Endpoints (Reads directly from PostgreSQL container)
@app.get("/tasks", summary="List All Tasks", tags=["Tasks"])
def get_tasks():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks ORDER BY id ASC;")
            rows = cursor.fetchall()
            return [{"id": row["id"], "title": row["title"], "done": row["done"]} for row in rows]
