import os
import re
import json
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
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

client = OpenAI(base_url=base_url, api_key=api_key)

PROMPT_FILE = Path(__file__).parent / "prompts" / "triage-v1.md"

def get_system_prompt() -> str:
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


# 1. Custom 400 Bad Request Handler for Input
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    field = errors[0]["loc"][-1] if errors and "loc" in errors[0] else "body"
    msg = errors[0]["msg"] if errors else "Invalid input"
    return JSONResponse(
        status_code=400,
        content={"error": f"Validation failed on field '{field}': {msg}"}
    )

# 2. JSON Cleaning & Validation Helper
def parse_and_validate(raw_text: str) -> tuple[TriageResponse | None, str | None]:
    # Strip markdown code fences if present
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    # Locate JSON object boundaries
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

# 3. Quarantine Logger
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

@app.get("/", summary="API Root", tags=["General"])
def read_root():
    return {
        "status": "online",
        "service": "support-triage-ai",
        "model": model_name,
        "endpoints": ["/triage", "/health"]
    }

@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "ok"}

@app.post("/triage", response_model=TriageResponse, summary="Triage Customer Support Message", tags=["AI Triage"])
async def triage_message(payload: TriageRequest):
    # Stub Mode
    if os.environ.get("LLM_STUB") == "1":
        return TriageResponse(
            category=CategoryEnum.BILLING,
            urgency=UrgencyEnum.NORMAL,
            confidence=0.95,
            reason="[STUB] Predefined classification for development testing."
        )

    # First Attempt
    current_prompt = get_system_prompt()
    messages = [
        {"role": "system", "content": current_prompt},
        {"role": "user", "content": payload.text}
    ]
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            temperature=0.0,
            messages=messages
        )
        raw_output = response.choices[0].message.content or ""
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {str(exc)}")

    validated_obj, err = parse_and_validate(raw_output)
    if validated_obj:
        return validated_obj

    # Repair Retry (Once and Only Once)
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

    try:
        repair_res = client.chat.completions.create(
            model=model_name,
            temperature=0.0,
            messages=repair_messages
        )
        repaired_raw = repair_res.choices[0].message.content or ""
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM repair call failed: {str(exc)}")

    repaired_obj, repair_err = parse_and_validate(repaired_raw)
    if repaired_obj:
        print("[REPAIR SUCCESS] Model corrected its output!")
        return repaired_obj

    # Quarantine on Unfixable Failure
    print(f"[QUARANTINE] Repair attempt also failed: {repair_err}. Quarantining...")
    log_quarantine(payload.text, repaired_raw, repair_err)
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Model output could not be validated against schema after repair attempt",
            "details": repair_err
        }
    )