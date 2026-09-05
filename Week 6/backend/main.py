import os
import re
import json
import time
import random
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError, AuthenticationError
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from src.llm.schema import TriageRequest, TriageResponse, CategoryEnum, UrgencyEnum

load_dotenv()

app = FastAPI(
    title="Production LLM Triage API",
    version="1.0",
    description="A resilient customer support message triage API backed by an LLM."
)

base_url = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
api_key = os.environ.get("LLM_API_KEY", "")
model_name = os.environ.get("LLM_MODEL", "openrouter/free")

# Explicit timeout (30s) and max_retries=0 so our custom retry policy is in control
client = OpenAI(base_url=base_url, api_key=api_key, timeout=30.0, max_retries=0)

PROMPT_FILE = Path(__file__).parent / "prompts" / "triage-v1.md"

def get_system_prompt() -> str:
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    field = errors[0]["loc"][-1] if errors and "loc" in errors[0] else "body"
    msg = errors[0]["msg"] if errors else "Invalid input"
    return JSONResponse(
        status_code=400,
        content={"error": f"Validation failed on field '{field}': {msg}"}
    )

def parse_and_validate(raw_text: str) -> tuple[TriageResponse | None, str | None]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return None, "No JSON object found in model output"

    try:
        data = json.loads(match.group(0))
    except Exception as e:
        return None, f"JSON parse error: {str(e)}"

    try:
        validated = TriageResponse(**data)
        return validated, None
    except ValidationError as ve:
        return None, f"Schema validation error: {str(ve)}"

def log_quarantine(input_text: str, raw_output: str, error_msg: str):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "quarantine.jsonl"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": "triage-v1",
        "input_text": input_text,
        "raw_output": raw_output,
        "error": error_msg
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# Structured Cost & Usage Logger
def log_usage(prompt_version: str, model: str, prompt_tokens: int, completion_tokens: int, duration_ms: float, repairs: int):
    log_entry = {
        "event": "llm_call",
        "prompt_version": prompt_version,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "duration_ms": round(duration_ms, 2),
        "repair_count": repairs
    }
    print(f"[METRICS] {json.dumps(log_entry)}")

# Robust Model Caller with Exponential Backoff + Jitter
def call_model_with_retries(messages: list[dict], max_attempts: int = 2):
    last_exception = None
    for attempt in range(1, max_attempts + 1):
        try:
            return client.chat.completions.create(
                model=model_name,
                temperature=0.0,
                messages=messages
            )
        except AuthenticationError as auth_err:
            # 401 Unauthorized: Fail immediately, NEVER retry
            print(f"[AUTH ERROR] HTTP 401 Invalid API key. Skipping retries.")
            raise HTTPException(status_code=401, detail="Invalid LLM provider API key")
        except (RateLimitError, APIConnectionError, APIStatusError) as err:
            status_code = getattr(err, "status_code", 500)
            # Never retry client errors (400, 403, 404)
            if status_code in (400, 403, 404):
                print(f"[CLIENT ERROR] HTTP {status_code}. Skipping retries.")
                raise HTTPException(status_code=status_code, detail=str(err))
            
            last_exception = err
            if attempt < max_attempts:
                # Exponential backoff with jitter
                sleep_time = (2 ** attempt) + random.uniform(0.1, 0.5)
                print(f"[RETRY WARNING] HTTP {status_code}. Retrying in {sleep_time:.2f}s (attempt {attempt}/{max_attempts})...")
                time.sleep(sleep_time)
            else:
                print(f"[FAIL] All {max_attempts} attempts failed.")
        except Exception as generic_err:
            if "timeout" in str(generic_err).lower():
                raise HTTPException(status_code=504, detail="LLM request timed out after 30s")
            raise generic_err

    if last_exception:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(last_exception)}")

@app.get("/", summary="API Root", tags=["General"])
def read_root():
    return {
        "status": "online",
        "service": "support-triage-ai",
        "model": model_name,
        "kill_switch_active": os.environ.get("LLM_ENABLED", "true").lower() == "false",
        "endpoints": ["/triage", "/health"]
    }

@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "ok"}

@app.post("/triage", response_model=TriageResponse, summary="Triage Customer Support Message", tags=["AI Triage"])
async def triage_message(payload: TriageRequest):
    # 1. Kill Switch Check
    if os.environ.get("LLM_ENABLED", "true").lower() == "false":
        print("[KILL SWITCH] LLM_ENABLED=false. Returning deterministic fallback.")
        return TriageResponse(
            category=CategoryEnum.OTHER,
            urgency=UrgencyEnum.NORMAL,
            confidence=0.5,
            reason="[FALLBACK] AI triage is currently disabled via system kill switch."
        )

    # 2. Stub Mode Check
    if os.environ.get("LLM_STUB") == "1":
        return TriageResponse(
            category=CategoryEnum.BILLING,
            urgency=UrgencyEnum.NORMAL,
            confidence=0.95,
            reason="[STUB] Predefined classification for development testing."
        )

    start_time = time.perf_counter()
    repair_count = 0
    current_prompt = get_system_prompt()
    
    messages = [
        {"role": "system", "content": current_prompt},
        {"role": "user", "content": payload.text}
    ]

    # First Call
    response = call_model_with_retries(messages)
    raw_output = response.choices[0].message.content or ""
    
    validated_obj, err = parse_and_validate(raw_output)
    if validated_obj:
        duration_ms = (time.perf_counter() - start_time) * 1000
        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        comp_tokens = usage.completion_tokens if usage else 0
        log_usage("triage-v1", model_name, prompt_tokens, comp_tokens, duration_ms, repairs=0)
        return validated_obj

    # Repair Retry (Once)
    repair_count += 1
    print(f"[REPAIR RETRY] Output failed validation: {err}. Asking model to repair...")
    repair_messages = [
        {"role": "system", "content": current_prompt},
        {"role": "user", "content": payload.text},
        {"role": "assistant", "content": raw_output},
        {
            "role": "user",
            "content": f"Your previous response was rejected for this reason: {err}. Return ONLY a corrected JSON object matching the schema."
        }
    ]

    repair_res = call_model_with_retries(repair_messages)
    repaired_raw = repair_res.choices[0].message.content or ""

    repaired_obj, repair_err = parse_and_validate(repaired_raw)
    duration_ms = (time.perf_counter() - start_time) * 1000

    if repaired_obj:
        print("[REPAIR SUCCESS] Model corrected its output!")
        usage = repair_res.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        comp_tokens = usage.completion_tokens if usage else 0
        log_usage("triage-v1", model_name, prompt_tokens, comp_tokens, duration_ms, repairs=1)
        return repaired_obj

    # Quarantine on Failure
    print(f"[QUARANTINE] Repair failed: {repair_err}. Quarantining...")
    log_quarantine(payload.text, repaired_raw, repair_err)
    return JSONResponse(
        status_code=422,
        content={
            "error": "Model output could not be validated against schema after repair attempt",
            "details": repair_err
        }
    )