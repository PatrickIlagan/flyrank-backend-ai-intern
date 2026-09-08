# Week 6

## Goals
- Learn production LLM integration patterns: treating models as slow, untrusted external APIs.
- Build a structured classification API endpoint with strict Pydantic input and output schemas.
- Implement versioned prompt specifications, repair retries, and quarantine logs.
- Add production safeguards: explicit timeouts, smart retries, cost logging, and a kill switch.
- Benchmark reliability with an 8-case evaluation set.

## Tasks
- [x] **Backend Track: Put an LLM Behind Your API (Assignment A17)**: Built a production-hardened customer support triage endpoint with Pydantic schema validation, repair retries, timeout/retry policy, kill switch, and an 8-case evaluation benchmark (100% accuracy). See `backend/`.
- [ ] **AI Fluency Track**: See `fluency/`.

## Experience Notes

### My Experience
I love AI in general and what it can bring to development and efficiency. Integrating AI's was already an integral part in my time in developing or making my own projects and applications. This time though, I was able to kind of get a grasp of where AI integration might actually do best like for sorting out backend requests like these in customer service. It was also super nice to see the limits and the strengths of what AI can actually do when it comes to categories, responses or basically the AI's thinking for certain prompts.

### Key Takeaways
- **LLMs as Untrusted HTTP Services**: Recognizing that an LLM is a non-deterministic, slow external API that must be bound by strict schemas, timeouts, and validation rules.
- **Contract-First Engineering**: Specifying closed enums and output shapes in `JOB-CARD.md` and Pydantic before touching prompt files or model calls.
- **Prompt Engineering as Code**: Versioning prompts as files (`triage-v1.md`) with explicit role boundaries, unsure handling, and few-shot examples rather than hardcoding loose strings in route handlers.
- **Production Defenses**: Enforcing short timeouts, smart non-retry on 401s, repair retry loops, quarantine logs (`quarantine.jsonl`), and a kill switch (`LLM_ENABLED=false`).

## Notes
- Full project code, setup guide, and documentation live in `backend/`.



