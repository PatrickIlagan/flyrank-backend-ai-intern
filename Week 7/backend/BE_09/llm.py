import os
from typing import Tuple
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip() or None
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

# Initialize OpenAI client if key is available
client = None
if OPENAI_API_KEY:
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )

def evaluate_decision(prompt: str, context: str) -> Tuple[str, str]:
    """
    Evaluates a node prompt against the provided input context using an LLM.
    Returns a tuple: (decision, reasoning_snippet)
    Decision is strictly 'YES' or 'NO'.
    """
    if not client:
        # Mock evaluator fallback when OPENAI_API_KEY is not configured
        prompt_lower = prompt.lower()
        context_lower = context.lower()

        # Simple semantic heuristic for testing without paid API keys
        positive_cues = ["support", "help", "broken", "issue", "crash", "refund", "yes", "urgent", "error", "problem"]
        has_positive = any(cue in context_lower for cue in positive_cues if cue in prompt_lower or cue in context_lower)
        
        # Check direct keyword overlap
        prompt_words = [w for w in prompt_lower.replace("?", "").split() if len(w) > 3]
        matches = [w for w in prompt_words if w in context_lower]
        
        decision = "YES" if (matches or has_positive) else "NO"
        reason = f"[Mock LLM - No API Key] Heuristic evaluation matched {len(matches)} keywords between prompt and context."
        return decision, reason

    # Real LLM call via OpenAI SDK
    system_instruction = (
        "You are an AI decision engine in an automated workflow. "
        "Given the user context and the decision question, decide if the answer is YES or NO. "
        "You must respond with ONLY the word YES or NO. "
        "No punctuation, no explanations, no extra characters."
    )
    user_message = f"User Context:\n{context}\n\nDecision Question:\n{prompt}"

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            temperature=0.0,
            max_tokens=5
        )
        raw_text = response.choices[0].message.content or ""
        cleaned = raw_text.strip().upper()
        
        if "YES" in cleaned:
            return "YES", f"[OpenAI {OPENAI_MODEL}] LLM evaluated decision to YES."
        elif "NO" in cleaned:
            return "NO", f"[OpenAI {OPENAI_MODEL}] LLM evaluated decision to NO."
        else:
            return "NO", f"[OpenAI {OPENAI_MODEL}] Ambiguous output '{raw_text}', defaulted to NO."
    except Exception as e:
        return "NO", f"[OpenAI Error Fallback] Failed LLM call: {str(e)}. Defaulted to NO."
