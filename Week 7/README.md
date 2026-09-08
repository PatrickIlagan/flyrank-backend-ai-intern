# Week 7

## Goals
- Master durable execution and background processing architectures using Inngest and FastAPI.
- Decouple slow tasks from user-facing HTTP requests via HTTP 202 Accepted and polling.
- Implement automated retries with exponential backoff for transient failures.
- Build scheduled background automation using cron expressions.

## Tasks
- [x] **Backend Track: Your First Background Job (BE_06 / Assignment A7)**: Fast 202 endpoint, Inngest background workers, retries, and cron schedules. See `backend/BE_06/`.
- [ ] **Backend Track: BE_08**: See `backend/BE_08/`.
- [ ] **AI Fluency Track**: See `fluency/`.

## Experience Notes

### My Experience
I have never heard of Inngest before and how it's actually really useful. I've used only like redis so this was quite new to me and this was actually pretty neat, especially when it comes with its own dev server. It's really useful honestly especially for those web applications that have heavy workloads who needs background actions running especially for testing or in development phase. I also noticed that for all of these assignments, there is a pattern of first initializing, creating the action, employing safeguards and error handling so that's really something I should be more aware to.

### Key Takeaways
- **Decoupling Latency via 202 Accepted and Eventual Consistency**: Moving slow tasks (like 8-second report builds) out of the request-response cycle by returning HTTP 202 Accepted immediately with an ID and polling status later.
- **Durable Orchestration without Redis / Celery Overhead**: Using Inngest to manage multi-step background workflows, where intermediate step outputs are memoized and paused without holding open synchronous server connections or maintaining separate message brokers.
- **Transient Failures vs Bad Input**: Rejecting permanent bad input at the door with HTTP 400 Bad Request (no background job created), while reserving automated retries and exponential backoff for transient system/service hiccups.
- **Autonomous Clock-Driven Automation**: Running scheduled background maintenance using cron expressions (`* * * * *`, `0 8 * * *`) that trigger strictly on schedule without requiring user endpoints.
- **The Core Backend Pattern**: Consistently applying the pattern across backend features: initializing clients, executing actions, employing defensive validation safeguards, and handling edge-case errors.

## Notes
- Full project code, setup guides, and documentation live in their respective subdirectories.
