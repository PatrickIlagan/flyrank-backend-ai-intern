# Week 3: Connecting Your CRUD to the Database

## Overview
Migrate the in-memory CRUD REST API from Week 2 onto a persistent SQLite database (tasks.db). The API endpoints and status codes remain identical to clients, but task data now survives server reboots.

## Stages & Checklist
- [ ] **Stage 0: Create SQLite Database**: Initialize tasks.db, create tasks table if not exists, and seed 3 default tasks only when empty.
- [ ] **Stage 1: Database Read Endpoints**: Query tasks.db with SQL SELECT for GET /tasks and GET /tasks/{id} (parameterized query).
- [ ] **Stage 2: Insert into Database**: Execute parameterized SQL INSERT for POST /tasks and return 201 Created with database-assigned ID.
- [ ] **Stage 3: Update and Delete with SQL**: Execute parameterized UPDATE and DELETE queries, preserving 200, 204, 400, and 404 status codes.
- [ ] **Stage 4: Explored SQLite**: Inspect tasks.db in DB Browser for SQLite and run manual SQL queries.
- [ ] **Stage 5: Database Documentation**: Complete documentation with why SQLite was chosen, run commands, SQL query example, and DB Browser screenshot.
- [ ] **Stage 6 / Extras (Optional)**: SQL search with LIKE, status filtering, SQL stats, timestamps, and AI Rematch diff.

## Quickstart

### 1. Set Up Virtual Environment
`powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
`

### 2. Install Dependencies
`powershell
pip install -r requirements.txt
`

### 3. Run the Server
`powershell
uvicorn main:app --reload --port 8000
`
