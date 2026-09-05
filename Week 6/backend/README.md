# Put an LLM Behind Your API (Production Triage Endpoint)

A production-hardened LLM integration built in Python 3.11 with FastAPI, Pydantic, and the OpenAI SDK. The endpoint accepts messy incoming customer support messages, queries a Large Language Model behind a strict schema, repairs malformed JSON, and enforces timeouts, smart retries, cost logging, and a kill switch.

Part of FlyRank AI Backend Engineering Internship: Week 6 (Assignment A17: Put an LLM behind your API).

---

## Stages & Checklist
- [x] Stage 0: Pick the Job, and Make a Model Answer You (JOB-CARD.md, provider configured, hello.py verified)
- [x] Stage 1: Build the Endpoint Before the AI (FastAPI POST /triage, input validation, output schema, stub mode)
- [x] Stage 2: The Prompt is a Specification (prompts/triage-v1.md with role, closed enums, unsure guidelines, and few-shot examples)
- [ ] Stage 3: Make the Output Trustworthy (parse, validate, repair retry once, quarantine on failure)
- [ ] Stage 4: Fit for Production (timeout, retry policy, cost logging, kill switch)
- [ ] Stage 5: Eval Set & Publish (evals/cases.json, benchmark score, final README)

---

## 🧪 Verified Stage 2 Live Responses

### 1. Off-Topic / Ambiguous Query (Hitting the Unsure Rule)
```bash
curl.exe -i -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"text": "Hey what is the weather like in Tokyo today?"}'
```
```json
{
  "category": "other",
  "urgency": "low",
  "confidence": 0.2,
  "reason": "The message asks about weather conditions in Tokyo, which is unrelated to software support topics like billing, bugs, or features."
}
```
*(Notice confidence is 0.2, strictly adhering to the "when unsure" rule).*

