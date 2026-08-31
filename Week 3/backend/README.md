# 🗄️ Week 3 Backend Track: Databases & Containerization

Welcome to Week 3 of the Backend Track for the **FlyRank AI Backend Engineering Internship**.

This week covers the evolution of API persistence across two dedicated assignments:

---

## 📂 Project Structure

`
Week 3/backend/
├── BE_W3A2/ (Assignment A2: Connecting your CRUD to the database)
│   ├── main.py (FastAPI + SQLite CRUD implementation)
│   ├── requirements.txt
│   ├── db_screenshot.png (DB Browser inspection)
│   └── README.md
│
└── BE_W3A3/ (Assignment A3: Containerize your stack)
    ├── main.py (FastAPI + PostgreSQL CRUD implementation)
    ├── Dockerfile (Container recipe for FastAPI)
    ├── compose.yaml (Multi-container orchestration for API + Postgres)
    ├── requirements.txt
    ├── .env.example
    └── README.md
`

---

## 🗺️ Assignment Summaries

### 1. [Assignment A2: Connecting your CRUD to SQLite (BE_W3A2/)](BE_W3A2/README.md)
- Replaced in-memory Python list with a single-file SQLite database (	asks.db).
- Parameterized SQL queries using ? placeholders to defend against SQL Injection.
- Hand-inspected and queried the database via DB Browser for SQLite.

### 2. [Assignment A3: Containerize your stack (BE_W3A3/)](BE_W3A3/README.md)
- Upgraded the storage layer to a full PostgreSQL database running inside an isolated Docker container.
- Connected FastAPI via psycopg and managed credentials using .env and .env.example.
- Packaged the API in a Dockerfile and orchestrated the entire stack with compose.yaml (docker compose up).

---

## 💭 Experience Notes

### My Experience
This is a really valuable experience for me since I know these are industry standards, I'm not new to both of these but haven't really learned the full essence of it. I used to use SQLite for mobile programming before so all of Assignment 2's was actually kinda familiar for me despite having different syntax, I was still able to get the hang of it fast. I didn't really fully understood before on why API requests or why having SQLite was actually important and just basically just learned the technicality of it, so with this assignment, I really understood every part on why it is important with the help of steps by steps and AI. As for Assignment 3, this is actually my first time touching dockers manually or by seeing it all work together, because before I just let Agentic AI's do it so it was really interesting for me to see it getting built with a docker. I now know how important dockers, environments, git workflows in an actual industry setting and I'm so glad to have atleast made one proper kind of program using PostgreSQL.

### Key Takeaways
- **Separation of Concerns**: The API routes remain identical regardless of whether data is stored in memory, SQLite, or PostgreSQL.
- **Reproducible Infrastructure**: Docker Compose eliminates "works on my machine" issues by packaging both code and database services into a single reproducible stack.
- **Environment Hygiene**: Strict separation of local secrets (.env) from public repositories using .env.example.
