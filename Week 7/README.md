# Week 7

## Goals
- Master durable execution and background processing architectures using Inngest and FastAPI.
- Decouple slow tasks from user-facing HTTP requests via HTTP 202 Accepted and polling.
- Implement automated retries with exponential backoff for transient failures.
- Build scheduled background automation using cron expressions.

## Tasks
- [x] **Backend Track: Your First Background Job (BE_06 / Assignment A7)**: Fast 202 endpoint, Inngest background workers, retries, and cron schedules. See `backend/BE_06/`.
- [x] **Backend Track: PDF Report Generator (BE_08 / Assignment A8)**: SQL aggregation, HTML print CSS layout, Playwright headless Chromium PDF generation, link-based distribution, and daily idempotency. See `backend/BE_08/`.
- [ ] **AI Fluency Track**: See `fluency/`.

## Experience Notes

### BE_06: Your First Background Job
I have never heard of Inngest before and how it's actually really useful. I've used only like redis so this was quite new to me and this was actually pretty neat, especially when it comes with its own dev server. It's really useful honestly especially for those web applications that have heavy workloads who needs background actions running especially for testing or in development phase. I also noticed that for all of these assignments, there is a pattern of first initializing, creating the action, employing safeguards and error handling so that's really something I should be more aware to.

### BE_08: PDF Report Generator
This is probably one of the most useful assignments ever as generating reports are probably one of the most efficient things ever. I got to learn about chromium headless and its pdf rendering using CSS and HTML which was something a bit more different. It's not the first time I've encountered or used this before but it was definitely an assignment where it made me realize how important it could actually be to those in different departments for companies.

### Key Takeaways
- **Decoupling Latency via 202 Accepted and Eventual Consistency**: Moving slow tasks (like 8-second report builds) out of the request-response cycle by returning HTTP 202 Accepted immediately with an ID and polling status later.
- **Durable Orchestration without Redis / Celery Overhead**: Using Inngest to manage multi-step background workflows, where intermediate step outputs are memoized and paused without holding open synchronous server connections or maintaining separate message brokers.
- **Transient Failures vs Bad Input**: Rejecting permanent bad input at the door with HTTP 400 Bad Request (no background job created), while reserving automated retries and exponential backoff for transient system/service hiccups.
- **Autonomous Clock-Driven Automation**: Running scheduled background maintenance using cron expressions (`* * * * *`, `0 8 * * *`) that trigger strictly on schedule without requiring user endpoints.
- **The Core Backend Pattern**: Consistently applying the pattern across backend features: initializing clients, executing actions, employing defensive validation safeguards, and handling edge-case errors.
- **SQL Aggregation over Memory Bloat (BE_08)**: Computing summary metrics directly in the database (`COUNT`, `SUM`, `AVG`, `GROUP BY`) rather than transferring thousands of raw rows into Python memory.
- **Headless Chromium Print Engine (BE_08)**: Generating multi-page PDFs using Playwright and Chromium's native print engine with HTML/CSS, providing a far more flexible, modern, and reliable layout system than archaic PDF libraries.
- **CSS Print Media Essentials (BE_08)**: Using `page-break-inside: avoid` on rows/cards and `thead { display: table-header-group; }` on tables to prevent broken rows and ensure repeating table headers across pages.
- **Link-Based File Distribution & Daily Idempotency (BE_08)**: Serving heavy binary documents by link (`FileResponse`) rather than JSON payload embedding, and shielding expensive rendering engines behind daily idempotency checks.

## Notes
- Full project code, setup guides, and documentation live in their respective subdirectories.
