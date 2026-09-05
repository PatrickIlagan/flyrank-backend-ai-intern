# Put an LLM Behind Your API (Production Triage Endpoint)

A production-hardened LLM integration built in Python 3.11 with FastAPI, Pydantic, and the OpenAI SDK. The endpoint accepts messy incoming customer support messages, queries a Large Language Model behind a strict schema, repairs malformed JSON, and enforces timeouts, smart retries, cost logging, and a kill switch.

Part of FlyRank AI Backend Engineering Internship: Week 6 (Assignment A17: Put an LLM behind your API).

---

## Stages & Checklist
- [ ] Stage 0: Pick the Job, and Make a Model Answer You
- [ ] Stage 1: Build the Endpoint Before the AI
- [ ] Stage 2: The Prompt is a Specification
- [ ] Stage 3: Make the Output Trustworthy
- [ ] Stage 4: Fit for Production
- [ ] Stage 5: Eval Set & Publish
