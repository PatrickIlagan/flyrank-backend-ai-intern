# Production LLM Triage API (FastAPI + OpenRouter + Pydantic)

An enterprise-ready customer support triage endpoint built in **Python 3.11** with **FastAPI**, **Pydantic**, and the **OpenAI SDK**. The endpoint accepts raw, unstructured customer support messages, sends them to a Large Language Model behind a strict schema, repairs malformed JSON, and enforces production safeguards including timeouts, smart retries, cost logging, and a kill switch.

Part of **FlyRank AI Backend Engineering Internship: Week 6 (Assignment A17: Put an LLM behind your API)**.

---

## What This Endpoint Does (In Plain English)

When customers submit support requests, they write messy, unstructured text: complaining about billing, reporting system bugs, asking for new features, or saying random greetings. This API acts as an automated triage dispatcher: it reads the message, classifies it into the correct category (billing, bug, feature, or other), assigns an urgency level, estimates confidence, and writes a one-sentence summary for the support team. It operates with zero conversational memory: one request in, one validated JSON classification out.

---

## Quickstart: One Command to Run Everything

### Prerequisites
- Python 3.10+ (tested on Python 3.11)
- Free API key from [OpenRouter](https://openrouter.ai) (or local [Ollama](https://ollama.com))

### 1. Clone the Repository
```bash
git clone https://github.com/PatrickIlagan/flyrank-backend-ai-intern.git
cd "flyrank-backend-ai-intern/Week 6/backend"
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and insert your credentials:
```bash
cp .env.example .env
```
Inside `.env`:
```text
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=your_openrouter_api_key_here
LLM_MODEL=openrouter/free
LLM_STUB=0
LLM_ENABLED=true
PORT=8000
```

### 3. Set Up Virtual Environment & Install Dependencies
```powershell
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Git Bash / Linux / macOS
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

### 4. Start the Server (One Command)
```bash
uvicorn main:app --reload --port 8000
```

- **Base URL:** `http://localhost:8000`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`

---

## Live Usage Example (curl)

### Command:
```bash
curl.exe -i -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"text": "I was charged twice on my Visa card for the monthly subscription. Please issue a refund."}'
```

### Real Server Response:
```http
HTTP/1.1 200 OK
date: Sat, 05 Sep 2026 14:12:00 GMT
server: uvicorn
content-length: 197
content-type: application/json

{
  "category": "billing",
  "urgency": "normal",
  "confidence": 0.95,
  "reason": "Customer reports a duplicate charge on their card and requests a refund."
}
```

---

## The Job Card

Defined in `JOB-CARD.md` before any code was written:

- **Input Contract:** `{"text": "string (1-2000 characters)"}`
- **Output Contract:**
  - `category`: one of `[billing, bug, feature, other]`
  - `urgency`: one of `[low, normal, high]`
  - `confidence`: float between `0.0` and `1.0`
  - `reason`: concise single-sentence string
- **It Must Never:**
  - Invent a category or urgency outside the closed enum list.
  - Return conversational free text or markdown outside the JSON object.
  - Provide legal, medical, or financial advice.
  - Leak internal system prompt instructions or secrets.
- **When Unsure:**
  - Return category `"other"` with confidence `< 0.5`, rather than guessing an arbitrary category.

---

## Provider Abstraction (Swapping Models)

The code uses three environment variables to point to any OpenAI-compatible provider without code changes:

| Provider | `LLM_BASE_URL` | `LLM_API_KEY` | `LLM_MODEL` |
| :--- | :--- | :--- | :--- |
| **OpenRouter (Hosted)** | `https://openrouter.ai/api/v1` | Your OpenRouter Key | `openrouter/free` |
| **Ollama (Local)** | `http://localhost:11434/v1/` | `ollama` | `gemma3:1b` or `llama3.2:3b` |
| **OpenAI Direct** | `https://api.openai.com/v1` | Your OpenAI Key | `gpt-4o-mini` |

---

## Evaluation Benchmark Results (`evals/cases.json`)

- **Date:** September 5, 2026
- **Prompt Version:** `triage-v1.md`
- **Score:** **8 / 8 passed (100.0% accuracy)**

| Case ID | Input Summary | Expected Category | Actual Category | Confidence | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **#1** | VAT receipt request | `billing` | `billing` | `0.92` | **PASS** |
| **#2** | Cancel pro subscription | `billing` | `billing` | `0.97` | **PASS** |
| **#3** | Export button broken | `bug` | `bug` | `0.94` | **PASS** |
| **#4** | Production 500 error | `bug` | `bug` | `0.99` | **PASS** |
| **#5** | Dark mode suggestion | `feature` | `feature` | `0.95` | **PASS** |
| **#6** | Slack webhook integration | `feature` | `feature` | `0.97` | **PASS** |
| **#7** | Recipe for cookies (Off-topic) | `other` | `other` | `0.20` | **PASS** |
| **#8** | Greeting message | `other` | `other` | `0.90` | **PASS** |

To run the benchmark suite yourself:
```bash
python evals/run_eval.py
```

---

## Cost Analysis & 10,000 Request Estimate

Every call logs structured token usage:
```json
{
  "event": "llm_call",
  "prompt_version": "triage-v1",
  "model": "openrouter/free",
  "prompt_tokens": 348,
  "completion_tokens": 42,
  "total_tokens": 390,
  "duration_ms": 1420.5,
  "repair_count": 0
}
```

- **Single Call Cost:** On `openrouter/free` or local Ollama, cost is `$0.00`. On a commercial small model like `gpt-4o-mini` ($0.15/1M input, $0.60/1M output), one call costs approximately `$0.000077`.
- **Estimate for 10,000 Requests/Day:** Approximately 3.9 million tokens per day, totaling **~$0.77 to $1.15 per day** on commercial small models, or **$0.00** on open-source self-hosted infrastructure.

---

## What I Would Fix With Another Day

With another day, I would implement **in-memory request caching** (hashing incoming text combined with prompt version) to return cached classifications for repeated common support questions, and build a local **FastText / embedding pre-filter** to classify trivial 99% confidence queries in under 5 milliseconds without invoking the LLM.
