import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
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

# 1. User Registration (POST /auth/signup)
@app.post("/auth/signup", summary="Register a new user", tags=["Authentication"])
async def signup(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid or missing JSON body"})
    email = body.get("email")
    password = body.get("password")
    # Validate inputs
    if not email or not isinstance(email, str) or not email.strip():
        return JSONResponse(status_code=400, content={"error": "Email is required and cannot be empty"})
    if not password or not isinstance(password, str) or not password.strip():
        return JSONResponse(status_code=400, content={"error": "Password is required and cannot be empty"})
    try:
        # Call Supabase Auth sign up
        response = supabase.auth.sign_up({
            "email": email.strip(),
            "password": password.strip()
        })
        
        if not response.user:
            return JSONResponse(status_code=400, content={"error": "User creation failed"})
        return JSONResponse(
            status_code=201,
            content={
                "message": "User registered successfully",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": str(response.user.created_at)
                }
            }
        )
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
# 2. User Login (POST /auth/login)
@app.post("/auth/login", summary="Log in and get JWT token", tags=["Authentication"])
async def login(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid or missing JSON body"})
    email = body.get("email")
    password = body.get("password")
    # Validate inputs
    if not email or not password:
        return JSONResponse(status_code=400, content={"error": "Both email and password are required"})
    try:
        # Authenticate with Supabase Auth
        response = supabase.auth.sign_in_with_password({
            "email": str(email).strip(),
            "password": str(password).strip()
        })
        if not response.session or not response.session.access_token:
            return JSONResponse(status_code=401, content={"error": "Invalid login credentials"})
        return {
            "access_token": response.session.access_token,
            "token_type": "bearer",
            "expires_in": response.session.expires_in,
            "user": {
                "id": response.user.id,
                "email": response.user.email
            }
        }
    except Exception:
        return JSONResponse(status_code=401, content={"error": "Invalid login credentials"})