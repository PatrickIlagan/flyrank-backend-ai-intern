import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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

# HTTPBearer security scheme (extracts Bearer tokens cleanly)
security = HTTPBearer()

# Reusable Auth Dependency (The Guard)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return {
            "id": user.id,
            "email": user.email,
            "created_at": str(user.created_at)
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# 1. Root and Health Endpoints
@app.get("/", summary="API Root Descriptor", tags=["General"])
def read_root():
    return {
        "status": "online",
        "message": "Server running and connected to Supabase",
        "endpoints": ["/auth/signup", "/auth/login", "/auth/logout", "/protected/profile", "/protected/dashboard", "/public/info"]
    }

@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "ok"}


# 2. Public Open Route
@app.get("/public/info", summary="Public Open Information", tags=["Public"])
def public_info():
    return {
        "message": "Welcome stranger! This info is public.",
        "status": "unrestricted"
    }


# 3. Auth Routes (Signup, Login, Logout)
@app.post("/auth/signup", summary="Register a new user", tags=["Authentication"])
async def signup(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid or missing JSON body"})

    email = body.get("email")
    password = body.get("password")

    if not email or not isinstance(email, str) or not email.strip():
        return JSONResponse(status_code=400, content={"error": "Email is required and cannot be empty"})
    if not password or not isinstance(password, str) or not password.strip():
        return JSONResponse(status_code=400, content={"error": "Password is required and cannot be empty"})

    try:
        response = supabase.auth.sign_up({"email": email.strip(), "password": password.strip()})
        if not response.user:
            return JSONResponse(status_code=400, content={"error": "User creation failed"})

        return JSONResponse(
            status_code=201,
            content={
                "message": "User registered successfully",
                "user": {"id": response.user.id, "email": response.user.email, "created_at": str(response.user.created_at)}
            }
        )
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.post("/auth/login", summary="Log in and get JWT token", tags=["Authentication"])
async def login(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid or missing JSON body"})

    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return JSONResponse(status_code=400, content={"error": "Both email and password are required"})

    try:
        response = supabase.auth.sign_in_with_password({"email": str(email).strip(), "password": str(password).strip()})
        if not response.session or not response.session.access_token:
            return JSONResponse(status_code=401, content={"error": "Invalid login credentials"})

        return {
            "access_token": response.session.access_token,
            "token_type": "bearer",
            "expires_in": response.session.expires_in,
            "user": {"id": response.user.id, "email": response.user.email}
        }
    except Exception:
        return JSONResponse(status_code=401, content={"error": "Invalid login credentials"})


@app.post("/auth/logout", summary="Log out of session", tags=["Authentication"])
def logout(current_user: dict = Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    return Response(status_code=204)


# 4. Protected Routes (Protected by get_current_user Dependency)
@app.get("/protected/profile", summary="User Profile (Protected)", tags=["Protected"])
def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Access granted to protected profile",
        "user": current_user
    }


@app.get("/protected/dashboard", summary="User Dashboard (Protected)", tags=["Protected"])
def get_dashboard(current_user: dict = Depends(get_current_user)):
    return {
        "message": f"Welcome to your private dashboard, {current_user['email']}!",
        "user_id": current_user["id"],
        "analytics": {
            "tasks_count": 12,
            "completed_count": 8,
            "account_status": "active"
        }
    }