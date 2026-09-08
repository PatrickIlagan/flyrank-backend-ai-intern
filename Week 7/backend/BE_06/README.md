# Your First Background Job (FastAPI + Inngest)

A durable, event-driven background processing API built in **Python 3.11** with **FastAPI** and **Inngest**. The API decouples slow work (e.g. 8-second report generation) from user request cycles using HTTP `202 Accepted`, status polling, automated retries with backoff, and a scheduled cron heartbeat.

Part of **FlyRank AI Backend Engineering Internship: Week 7 (Assignment BE_06 / A7: Your first background job)**.

---

## Stages & Checklist
- [x] **Stage 0: Hello, Server**: Create FastAPI server with GET /health returning status 200.
- [x] **Stage 1: Connect Inngest**: Install Inngest SDK, define `say-hello` function, connect to Inngest Dev Server, and invoke from dashboard.
- [x] **Stage 2: The Fast Door (Accept Now, Work Later)**: POST /reports returns 202 immediately, sends event to `make-report` (8s sleep + build), and GET /reports/:id polls status until done.
- [x] **Stage 3: Jobs Fail, Watch the Retry**: Add failure simulation for topic "fail", configure retries=2, watch exponential backoff, and reject missing topics with 400.
- [x] **Stage 4: The Clock Knocks (Cron Heartbeat)**: Add scheduled `heartbeat` cron function running every minute (`* * * * *`) and audit report status.
- [ ] **Stage 5: Publish & Docs**: Complete documentation, add dashboard screenshots, verify clean clone instructions, and publish.

---

## Stage 3 Key Insight: Transient Failure vs Bad Input

A wrong input must be rejected at the door (HTTP 400); only a wrong moment (transient network or service failure) deserves a retry. Retrying a bad input 10 times will never make it valid, but retrying a transient glitch gives the external service time to recover.

---

## Stage 4: Cron Expressions

- **Every day at 08:00:** The cron expression is `0 8 * * *`, which triggers at minute 0 of hour 8 every day.
- **Every Sunday at 22:00:** The cron expression is `0 22 * * 0`, which triggers at minute 0 of hour 22 on Sunday.
