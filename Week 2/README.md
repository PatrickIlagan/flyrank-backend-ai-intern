# Week 2

## Goals
- Understand HTTP fundamentals, the request-response cycle, REST verbs, and standard HTTP status codes.
- Build an in-memory Task Management CRUD API step-by-step across 6 structured stages.
- Test and document endpoints using `curl` and interactive Swagger UI (`/docs`).
- Maintain a professional Git commit history (at least 6 stage commits) and write clear developer-facing documentation.

## Tasks
- [x] **Backend Track: Build Your First CRUD API (Assignment A1)**: Built complete in-memory Task Management CRUD API with FastAPI, validation, Swagger UI docs, and verified via `curl`. See `backend/`.
- [x] **AI Fluency Track (FL_04: Frame Your Work)**: Framed project case studies (PrismLearning.AI & Task API) using the 3-beat structure, defined personal voice card, crafted bio/CTA, and produced before/after comparisons. See `fluency/FL_04/`.
- [x] **AI Fluency Track (FL_05: The Prompt Ladder)**: Iterative prompt optimization from weak baseline to production-grade architecture across 5 single-layer rungs, including an honest brevity constraint regression and stranger-proof reusable prompt. See `fluency/FL_05/`.

## Experience Notes

### My Experience
As someone who has built with FastAPI in Python using AI without the basic knowledge, this has really helped me to understand what Python FastAPI can really do. It was a fun learning experience that finally made me fully understand what all of this is about. It made me truly understand how you could make CRUD endpoints, typing each syntax one by one and pretty much familiarizing myself for this. This is so useful and will definitely be a handy experience for my future projects!

### Key Takeaways
- Building endpoints step-by-step from scratch builds a real intuition for HTTP verbs (`GET`, `POST`, `PUT`, `DELETE`) and proper status codes (`200`, `201`, `204`, `400`, `404`, `500`).
- The value of defensive backend validation: never trusting client input and enforcing clean request structures.
- How OpenAPI and Swagger UI provide instant interactive documentation and API testing directly from code definitions.
- **Iterative Prompt Engineering (FL_05)**: Changing exactly one variable at a time (Goal, Context, Constraints, Format, Quality Criteria) to verify which ingredient created value versus regressions.
- **The Peril of Raw Constraints (FL_05)**: Naive brevity constraints force AI models to cut essential security guards (salts, error handling, token expiration) to save lines. Structure should be enforced via architectural file formats rather than line limits.

## Notes
- Full project code, setup guide, and documentation live in `backend/`.
- Framed case studies (.docx and .md deliverables) live in `fluency/FL_04/`.
- Prompt Ladder deliverables (.docx and .md deliverables) live in `fluency/FL_05/`.

