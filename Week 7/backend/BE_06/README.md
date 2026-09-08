# Your First Background Job (FastAPI + Inngest)

A durable, event-driven background processing API built in **Python 3.11** with **FastAPI** and **Inngest**. The API decouples slow work (e.g. 8-second report generation) from user request cycles using HTTP `202 Accepted`, status polling, automated retries with backoff, and a scheduled cron heartbeat.

Part of **FlyRank AI Backend Engineering Internship: Week 7 (Assignment BE_06 / A7: Your first background job)**.

---

## Stages & Checklist
- [ ] **Stage 0: Hello, Server**: Create FastAPI server with GET /health returning status 200.
- [ ] **Stage 1: Connect Inngest**: Install Inngest SDK, define `say-hello` function, connect to Inngest Dev Server, and invoke from dashboard.
- [ ] **Stage 2: The Fast Door (Accept Now, Work Later)**: POST /reports returns 202 immediately, sends event to `make-report` (8s sleep + build), and GET /reports/:id polls status until done.
- [ ] **Stage 3: Jobs Fail, Watch the Retry**: Add failure simulation for topic "fail", configure retries=2, watch exponential backoff, and reject missing topics with 400.
- [ ] **Stage 4: The Clock Knocks (Cron Heartbeat)**: Add scheduled `heartbeat` cron function running every minute (`* * * * *`) and audit report status.
- [ ] **Stage 5: Publish & Docs**: Complete documentation, add dashboard screenshots, verify clean clone instructions, and publish.
