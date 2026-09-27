# FL_05: The Prompt Ladder (Iterative Prompt Engineering)

**Author:** John Patrick Ilagan (Patrick)  
**Track:** AI Fluency Track: Week 2  
**Cohort:** FlyRank AI Backend Engineering Internship  
**Assignment:** The Prompt Ladder (FL_05 / Iterative Prompt Optimization)  

---

## Executive Summary

The gap between a lazy prompt and an engineered prompt is the cheapest, highest-leverage performance upgrade when building software with AI. Most engineers never experience this upgrade because they change multiple variables at once: tweaking wording, adding context, and imposing format rules simultaneously. When output changes, they cannot identify which ingredient created value and which caused regressions.

This document executes the **Prompt Ladder** methodology: starting from a genuinely weak baseline prompt from the backend engineering track, and climbing five disciplined rungs. Each rung introduces **exactly one named layer** chosen specifically to attack the previous output's biggest failure mode.

Across these six runs, outputs are compared side-by-side with four evaluation notes per version:
1. **What changed in the prompt** (the single named layer added).
2. **What actually improved in the output** (behavioral changes in the generated result, not just prompt prose).
3. **What still failed** (unresolved issues or newly uncovered bottlenecks).
4. **What to try next** (the logical next layer).

Crucially, this ladder includes an honest **"this made it worse"** regression (Version 3), proving that naive constraints often destroy code quality before structured formatting and quality criteria can salvage it. The document concludes with a fully engineered, reusable prompt ready for any backend engineer to use independently.

---

## The Prompt Ladder Overview

| Rung | Version | Named Layer Added | Primary Goal / Target Failure | Output Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **0** | **Baseline** | None (Raw Beginner Prompt) | Minimal prompt typed a month ago | Embarrassingly generic, obsolete Flask, insecure |
| **1** | **Version 1** | **Clearer Goal** | Target modern framework and auth flow | Switched to FastAPI + OAuth2, but monolithic |
| **2** | **Version 2** | **Real Context** | Connect to actual tech stack and database | Added async SQLAlchemy + Postgres, but huge dump |
| **3** | **Version 3** | **Constraints** *(Regression)* | Restrict output length to prevent bloat | **Degraded!** Cut security, salts, and error handling |
| **4** | **Version 4** | **Specified Output Format** | Restore structure via modular files | Clean 4-file separation, but missing edge cases |
| **5** | **Version 5** | **Quality Criteria** | Enforce RFC specs and security rigor | RFC 6749 compliant, 401/409 codes, production-ready |
| **Final** | **Reusable** | Packaged Template | Stranger-proof standalone prompt | Reusable by any backend engineer without guidance |

---

## Run 0: Baseline (The Weak Prompt)

### The Prompt
```text
Write backend code for user authentication.
```

### Representative Output Excerpt
```python
# Here is how you can do user authentication in Python using Flask!
from flask import Flask, request, jsonify
import sqlite3
import hashlib

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('users.db')
    return conn

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    # Hash password with SHA256
    password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password_hash))
    conn.commit()
    conn.close()
    return jsonify({"message": "User registered successfully!"})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({"message": "Login successful!"})
    return jsonify({"message": "Invalid credentials"}), 401

# You can also use cookies or sessions if you want to remember logged in users.
# For production, consider using libraries like Flask-Login or bcrypt!
if __name__ == '__main__':
    app.run(debug=True)
```

### Baseline Critique
- **Conversational filler:** 4 paragraphs of introductory essay on what authentication is and why apps need it.
- **Wrong framework:** Generated legacy synchronous Flask instead of modern async FastAPI.
- **Severe security vulnerabilities:** Used raw `hashlib.sha256` with zero salt, leaving passwords open to rainbow table attacks.
- **Toy database handling:** Creates the database table inside the HTTP request handler on every registration call.
- **No stateful tokens:** Login returns a plain JSON string with no session cookie, no bearer token, and no JWT.

---

## Run 1: Version 1 (Layer: Clearer Goal)

### The Single Change
- **Named Layer:** **Clearer Goal**
- **Rationale:** The biggest weakness of the baseline was that the LLM guessed the entire problem space: it chose Flask, picked basic SQL queries, and generated a toy greeting script. Defining a concrete objective forces the model to target a specific technology and protocol.

### The Version 1 Prompt
```text
Write backend code for user authentication. 

Goal: Build a user signup and login flow in FastAPI using the OAuth2 password bearer flow with signed JWT access tokens.
```

### Representative Output Excerpt
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

app = FastAPI()

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {}

class UserCreate(BaseModel):
    username: str
    password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/signup")
def signup(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": get_password_hash(user.password)
    }
    return {"msg": "User created"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}
```

### The Four Evaluation Notes
1. **What changed in the prompt:** Added a **Clearer Goal** specifying FastAPI, OAuth2 Password Bearer flow, and signed JWT access tokens.
2. **What actually improved in the output:** It completely stopped generating obsolete Flask code, eliminated the three-paragraph textbook essay about authentication, switched to modern `bcrypt` password hashing via `passlib`, and implemented standard OAuth2 bearer token responses (`access_token`, `token_type: "bearer"`).
3. **What still failed:** It relied on an in-memory dictionary (`fake_users_db = {}`) that loses all state on restart, hardcoded cryptographic secrets directly into the script, and mashed routes, hashing, and token math into a single monolithic script.
4. **What to try next:** Inject real context about our application architecture, database layer, and environment configuration.

---

## Run 2: Version 2 (Layer: Real Context)

### The Single Change
- **Named Layer:** **Real Context**
- **Rationale:** The Version 1 output is still a sandbox toy because the model has no knowledge of our infrastructure. Giving the model real operational context forces it to connect to our actual database engine, ORM, and runtime environment.

### The Version 2 Prompt
```text
Write backend code for user authentication. 

Goal: Build a user signup and login flow in FastAPI using the OAuth2 password bearer flow with signed JWT access tokens.

Context: This service is a production multi-tenant backend running on Python 3.11 with PostgreSQL. We use SQLAlchemy 2.0 with asyncpg for asynchronous sessions, Pydantic v2 for data validation, and python-jose with cryptography for JWT signing.
```

### Representative Output Excerpt
```python
import os
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from passlib.context import CryptContext
from jose import jwt, JWTError

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/app_db")
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-insecure-key")
ALGORITHM = "HS256"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    is_active: bool

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# ... [Output truncated after 120 lines of dense code, cutting off get_current_user implementation] ...
```

### The Four Evaluation Notes
1. **What changed in the prompt:** Added **Real Context** defining our production environment: Python 3.11, PostgreSQL, SQLAlchemy 2.0 `Mapped` columns, `asyncpg`, Pydantic v2 `ConfigDict(from_attributes=True)`, and `python-jose`.
2. **What actually improved in the output:** The fake in-memory dictionary disappeared; the code adopted real asynchronous database patterns (`AsyncSession`, `select(UserModel)`), updated Pydantic syntax to v2 standards, and extracted configuration from environment variables via `os.getenv`.
3. **What still failed:** The response became an overwhelming, 350-line wall of code that exhausted the output token window, truncated mid-function during JWT decoding, and crammed database models, password helpers, and endpoint routers into one unmaintainable file.
4. **What to try next:** Impose strict constraints to force the model to be concise and prevent token exhaustion.

---

## Run 3: Version 3 (Layer: Constraints) - The Honest Regression

> [!WARNING]
> **The Honest "This Made It Worse" Moment**: In this run, an aggressive negative constraint was added to stop the model from rambling and hitting token limits. The result was a dramatic regression: to obey the brevity rule, the LLM gutted essential security safeguards.

### The Single Change
- **Named Layer:** **Constraints**
- **Rationale:** The previous output was bloated, dumped everything into one file, and ran out of output tokens. To fix this, a strict brevity constraint was added: limit total code to under 60 lines and forbid explanations.

### The Version 3 Prompt
```text
Write backend code for user authentication. 

Goal: Build a user signup and login flow in FastAPI using the OAuth2 password bearer flow with signed JWT access tokens.

Context: This service is a production multi-tenant backend running on Python 3.11 with PostgreSQL. We use SQLAlchemy 2.0 with asyncpg for asynchronous sessions, Pydantic v2 for data validation, and python-jose with cryptography for JWT signing.

Constraint: Keep the entire implementation under 60 lines of code. Do not include any explanations, docstrings, or optional comments.
```

### Representative Output Excerpt
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from jose import jwt
import hashlib, os

app = FastAPI()
engine = create_async_engine(os.getenv("DATABASE_URL"))
session_maker = async_sessionmaker(engine)

class Base(DeclarativeBase): pass
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    pwd: Mapped[str] = mapped_column(String)

class AuthIn(BaseModel): email: EmailStr; password: str

async def get_db():
    async with session_maker() as s: yield s

@app.post("/signup")
async def signup(b: AuthIn, db: AsyncSession = Depends(get_db)):
    db.add(User(email=b.email, pwd=hashlib.md5(b.password.encode()).hexdigest()))
    await db.commit()
    return {"ok": True}

@app.post("/token")
async def token(f: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    u = (await db.execute(select(User).where(User.email == f.username))).scalar_one_or_none()
    if not u or u.pwd != hashlib.md5(f.password.encode()).hexdigest(): raise HTTPException(400)
    return {"access_token": jwt.encode({"sub": u.email}, "secret"), "token_type": "bearer"}
```

### The Four Evaluation Notes
1. **What changed in the prompt:** Added a negative **Constraint** restricting the total implementation to under 60 lines with no comments or explanations.
2. **What actually improved in the output:** **Nothing improved. This change actively degraded the solution.** While it achieved brevity, it achieved it by amputating software engineering integrity.
3. **What still failed (The Severe Regression):**
   - **Reverted to insecure hashing:** To save lines, the model threw away `passlib` and bcrypt, replacing them with raw, un-salted `hashlib.md5()`.
   - **Hardcoded secrets:** Replaced secure token signing with a hardcoded `"secret"` string.
   - **Bypassed expiration:** Removed JWT expiration (`exp`) timestamps entirely, generating permanent, irrevocable tokens.
   - **Dangerous error swallowing:** Replaced clean exception handling with blind `raise HTTPException(400)`.
   - **Conclusion:** Forcing brevity through raw line count constraints encourages AI to cut safety guards first.
4. **What to try next:** Eliminate the destructive line constraint and instead use a **Specified Output Format** that defines clean, modular files with designated boundaries.

---

## Run 4: Version 4 (Layer: Specified Output Format)

### The Single Change
- **Named Layer:** **Specified Output Format**
- **Rationale:** Replacing the negative line constraint with an architectural blueprint. Instead of telling the model to be "short," we tell it exactly which modular files to produce and what each file is responsible for.

### The Version 4 Prompt
```text
Write backend code for user authentication. 

Goal: Build a user signup and login flow in FastAPI using the OAuth2 password bearer flow with signed JWT access tokens.

Context: This service is a production multi-tenant backend running on Python 3.11 with PostgreSQL. We use SQLAlchemy 2.0 with asyncpg for asynchronous sessions, Pydantic v2 for data validation, and python-jose with cryptography for JWT signing.

Output Format: Output the solution strictly as four distinct modular files formatted in separate markdown code blocks with clear file path headings:
1. `app/core/security.py`: Password hashing and JWT generation/validation helpers.
2. `app/models/user.py`: SQLAlchemy 2.0 async User model.
3. `app/schemas/auth.py`: Pydantic v2 request/response schemas.
4. `app/api/v1/auth.py`: FastAPI APIRouter containing `/signup` and `/login` endpoints.
```

### Representative Output Excerpt

#### File 1: `app/core/security.py`
```python
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from passlib.context import CryptContext
from jose import jwt, JWTError
import os

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

#### File 2: `app/models/user.py`
```python
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

#### File 3: `app/schemas/auth.py`
```python
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserSignUp(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

#### File 4: `app/api/v1/auth.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.auth import UserSignUp, UserRead, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token
# Assuming get_db dependency exists in app.db.session
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserSignUp, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(email=payload.email, hashed_password=get_password_hash(payload.password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token)
```

### The Four Evaluation Notes
1. **What changed in the prompt:** Replaced the line constraint with a **Specified Output Format** detailing four exact file paths with dedicated responsibilities.
2. **What actually improved in the output:** The monolithic mess completely separated into standard production layers (security utilities, database models, Pydantic schemas, API router). The code can now be placed directly into an application directory tree without manual refactoring.
3. **What still failed:** Security error hygiene is deficient. Failed authentication returns HTTP 400 Bad Request instead of RFC-standard HTTP 401 Unauthorized with the mandatory `WWW-Authenticate: Bearer` header, and duplicate user creation returns HTTP 400 instead of HTTP 409 Conflict. Password complexity is unvalidated.
4. **What to try next:** Layer on concrete Quality Criteria enforcing RFC standards, defensive error codes, and strict password validation.

---

## Run 5: Version 5 (Layer: Quality Criteria)

### The Single Change
- **Named Layer:** **Quality Criteria**
- **Rationale:** The architecture is now clean, but backend engineering requires adherence to protocols and security standards. Defining explicit quality criteria ensures the code handles edge cases, security headers, and standard status codes defensively.

### The Version 5 Prompt
```text
Write backend code for user authentication. 

Goal: Build a user signup and login flow in FastAPI using the OAuth2 password bearer flow with signed JWT access tokens.

Context: This service is a production multi-tenant backend running on Python 3.11 with PostgreSQL. We use SQLAlchemy 2.0 with asyncpg for asynchronous sessions, Pydantic v2 for data validation, and python-jose with cryptography for JWT signing.

Output Format: Output the solution strictly as four distinct modular files formatted in separate markdown code blocks with clear file path headings:
1. `app/core/security.py`: Password hashing and JWT generation/validation helpers.
2. `app/models/user.py`: SQLAlchemy 2.0 async User model.
3. `app/schemas/auth.py`: Pydantic v2 request/response schemas.
4. `app/api/v1/auth.py`: FastAPI APIRouter containing `/signup` and `/login` endpoints.

Quality Criteria:
- RFC 6749 compliance: Failed login must return HTTP 401 Unauthorized with the header `WWW-Authenticate: Bearer`.
- Duplicate identity: Existing email on signup must return HTTP 409 Conflict with a structured error detail.
- Password hygiene: Enforce minimum 8 characters with at least one number and one uppercase letter using Pydantic field validators.
- Token security: Include `exp` timestamp in UTC, token type claim (`"type": "access"`), and handle `JWTError` explicitly.
- Inactive user check: Block authentication if `user.is_active` is False with HTTP 403 Forbidden.
```

### Representative Output Excerpt

#### File 3 Excerpt: `app/schemas/auth.py` (Validations Added)
```python
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
import re

class UserSignUp(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
```

#### File 4 Excerpt: `app/api/v1/auth.py` (Defensive Error Handling)
```python
@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserSignUp, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with email '{payload.email}' already exists."
        )
    
    new_user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )
        
    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token, expires_in=3600)
```

### The Four Evaluation Notes
1. **What changed in the prompt:** Added strict **Quality Criteria** covering RFC 6749 compliance, HTTP 409 Conflict, regex password validation, inactive user checking, and explicit JWT exception handling.
2. **What actually improved in the output:** Error responses conform to industry standards: failed logins return RFC-compliant 401 with `WWW-Authenticate: Bearer`, duplicate signups cleanly return 409 Conflict instead of generic 400s, inactive accounts are stopped with 403 Forbidden, and weak passwords fail at the Pydantic schema validation layer before touching database resources.
3. **What still failed:** The prompt is specific to my immediate mental context. A colleague on the backend track who wants to use this prompt for their own project would have to manually rewrite hardcoded assumptions and wouldn't know how to verify or wire the router into a FastAPI root app.
4. **What to try next:** Package this into a polished, stranger-proof reusable prompt with clear placeholders, stated assumptions, and end-to-end verification curl commands.

---

## Final Deliverable: The Standalone Reusable Prompt

This prompt is cleaned up, parameterized, and structured so that any backend engineer or intern can copy it, replace the bracketed placeholders, and generate production-grade authentication without needing assistance.

```markdown
You are a Staff Backend Engineer specializing in Python, FastAPI, and secure cloud API design.

### Objective
Implement a secure, production-ready user authentication and registration module using FastAPI and OAuth2 Password Bearer flow with signed JWT access tokens.

### Target Environment & Tech Stack
- Runtime: Python 3.11+
- Web Framework: FastAPI
- Database ORM: SQLAlchemy 2.0 (using `Mapped`, `mapped_column`, and asyncpg)
- Validation: Pydantic v2 (`field_validator`, `ConfigDict`)
- Cryptography: `passlib[bcrypt]` for password hashing and `python-jose[cryptography]` for JWT signing

### Required Output Structure
Output the complete implementation across four modular files using markdown code blocks with clear relative paths:
1. `[APP_DIR]/core/security.py`:
   - Password hashing and constant-time verification using bcrypt.
   - JWT access token creation with expiration and subject claims.
   - `SECRET_KEY` and `ALGORITHM` loaded safely from environment variables.
2. `[APP_DIR]/models/user.py`:
   - SQLAlchemy 2.0 `User` table definition with `id`, `email` (unique index), `hashed_password`, `is_active` (boolean default True), and `created_at` timestamp.
3. `[APP_DIR]/schemas/auth.py`:
   - `UserSignUp` schema enforcing email format and password strength (min 8 chars, at least one digit and one uppercase letter).
   - `UserRead` response schema with `ConfigDict(from_attributes=True)`.
   - `TokenResponse` schema returning `access_token`, `token_type` ("bearer"), and `expires_in`.
4. `[APP_DIR]/api/v1/auth.py`:
   - `APIRouter(prefix="/auth", tags=["Auth"])` mounting `/signup` (201 Created) and `/login` (OAuth2PasswordRequestForm).

### Quality & Security Criteria
- RFC 6749 Compliance: On failed authentication, return HTTP 401 Unauthorized with header `{"WWW-Authenticate": "Bearer"}`.
- Conflict Handling: Duplicate registration must catch existing emails and return HTTP 409 Conflict.
- Account Status: Inactive users (`is_active=False`) must be rejected with HTTP 403 Forbidden.
- Session Safety: Use asynchronous SQLAlchemy sessions with clean session rollback on unexpected exceptions.
- Zero Boilerplate Omission: Do not use placeholders like `# Implement here` or truncate code blocks. Provide complete, runnable code.

### Verification Deliverables
At the end of your response, provide exact `curl` commands to test:
1. Creating a new user via `POST /auth/signup`.
2. Attempting duplicate signup (expecting HTTP 409 Conflict).
3. Logging in with valid credentials via `POST /auth/login` (expecting Bearer token).
4. Logging in with bad password (expecting HTTP 401 with WWW-Authenticate header).
```

---

## 💡 Intern Reflection & Key Takeaways

1. **Prompt Engineering is Architectural Specification:** A vague prompt produces a toy script; a layered prompt produces software architecture. When an engineer complains that "AI only writes beginner code," it is almost always because their prompt provided beginner-level specifications.
2. **The Danger of Raw Constraints:** Negative line-count constraints are dangerous. They prompt the model to sacrifice defensive checks, password hashing complexity, and error handlers to meet an arbitrary length metric. Structure should be enforced through file blueprints, not line limits.
3. **One Layer at a Time:** By climbing the ladder one rung at a time, every ingredient earned its place. If we had added Goal, Context, Constraints, Format, and Quality Criteria all at once, we never would have discovered that the length constraint was actively poisoning our security architecture.
