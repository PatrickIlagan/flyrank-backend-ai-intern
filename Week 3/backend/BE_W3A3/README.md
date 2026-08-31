# Task Management Containerized API (PostgreSQL + Docker)

A persistent CRUD REST API built with **Python 3.11** and **FastAPI**, connected to a **PostgreSQL** database running inside a **Docker** container, orchestrated with **Docker Compose**.

Part of **FlyRank AI Backend Engineering Internship: Week 3 (Assignment A3: Containerize your stack)**.

---

## Stages & Checklist
- [ ] **Stage 0: Postgres in Docker + gitignore**: Start Postgres container on port 5432 with persistent volume and verify with psql.
- [ ] **Stage 1: Connect via .env and create table**: Connect FastAPI using psycopg and DATABASE_URL from .env, create tasks table, and seed 3 default tasks.
- [ ] **Stage 2: Read from Postgres**: Implement GET /tasks and GET /tasks/{id} with parameterized queries (%s placeholder) and 404 handling.
- [ ] **Stage 3: Full CRUD on Postgres**: Implement POST /tasks (INSERT with RETURNING), PUT /tasks/{id}, and DELETE /tasks/{id} (204 No Content).
- [ ] **Stage 4: Docker-Compose the Whole Stack**: Package the API with a Dockerfile and orchestrate API + Postgres with compose.yaml (one-command startup).
- [ ] **Stage 5: One-Command Stack + Docs**: Finalize documentation, verify .env is git-ignored, test clean clone startup, and push.
- [ ] **Stage 6 / Extras (Optional)**: Database health check, database mortality test, and AI Rematch diff.
