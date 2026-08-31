# Week 3

## Goals
- Connect the CRUD API to a persistent SQLite database (tasks.db) so data survives server restarts (Assignment A2).
- Containerize the application and a real PostgreSQL database using Docker and Docker Compose (Assignment A3).
- Manage configuration and secrets using .env and environment variables.
- Maintain atomic stage commits and complete developer-facing documentation.

## Tasks
- [x] **Backend Track: Connecting Your CRUD to the Database (Assignment A2)**: Migrated in-memory storage to SQLite, parameterized SQL queries, DB Browser inspection, and complete documentation. See `backend/BE_W3A2/`.
- [x] **Backend Track: Containerize Your Stack (Assignment A3)**: Run PostgreSQL in Docker, wire FastAPI with psycopg driver, compose the entire stack, and verify persistence across volume restarts. See `backend/BE_W3A3/`.
- [ ] **AI Fluency Track**: See `fluency/`.

## Experience Notes

### My Experience
This is a really valuable experience for me since I know these are industry standards, I'm not new to both of these but haven't really learned the full essence of it. I used to use SQLite for mobile programming before so all of Assignment 2's was actually kinda familiar for me despite having different syntax, I was still able to get the hang of it fast. I didn't really fully understood before on why API requests or why having SQLite was actually important and just basically just learned the technicality of it, so with this assignment, I really understood every part on why it is important with the help of steps by steps and AI. As for Assignment 3, this is actually my first time touching dockers manually or by seeing it all work together, because before I just let Agentic AI's do it so it was really interesting for me to see it getting built with a docker. I now know how important dockers, environments, git workflows in an actual industry setting and I'm so glad to have atleast made one proper kind of program using PostgreSQL.

### Key Takeaways
- **The Storage Ladder**: Moving from in-memory lists to SQLite files to PostgreSQL containers proved that the API interface is independent of the underlying storage engine.
- **Docker & Containerization**: Understanding how Docker and Docker Compose package dependencies and services so an entire multi-tier system spins up with a single command (`docker compose up`).
- **Secrets Hygiene**: Managing configuration safely via `.env` (git-ignored) and providing committed templates (`.env.example`) to prevent credential leaks.
- **Hands-on Understanding over AI Auto-Pilot**: Moving beyond letting AI generate code blindly to reading, testing, and debugging database drivers and container configurations step by step.

## Notes
- Full project code, setup guides, and documentation live in `backend/BE_W3A2/` and `backend/BE_W3A3/`.




