import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

base_url = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
api_key = os.environ.get("LLM_API_KEY", "")
model = os.environ.get("LLM_MODEL", "openrouter/free")

# If LLM_STUB=1 or api_key is dummy, allow offline testing
if os.environ.get("LLM_STUB") == "1" or not api_key:
    print("[STUB MODE] Model status: ready")
else:
    client = OpenAI(base_url=base_url, api_key=api_key)
    res = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Reply with exactly the word: ready"}],
    )
    print(res.choices[0].message.content)
