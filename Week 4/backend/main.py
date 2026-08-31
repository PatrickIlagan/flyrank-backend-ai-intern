import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import FastAPI

# 1. Load secrets from .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env file")

# 2. Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="Auth API (Supabase Auth)",
    version="1.0",
    description="A secure Authentication and Token Verification API backed by Supabase Auth."
)

# 3. Root Endpoint
@app.get("/", summary="API Root Descriptor", tags=["General"])
def read_root():
    return {
        "status": "online",
        "message": "Server running and connected to Supabase",
        "endpoints": ["/auth/signup", "/auth/login", "/auth/logout", "/protected/profile", "/public/info"]
    }

@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "ok"}
