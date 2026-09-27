# FL_02: Prompt Iteration Log and Cross-Model Comparison

**Author:** John Patrick Ilagan (Patrick)  
**Track:** AI Fluency Track: Week 2  
**Cohort:** FlyRank AI Backend Engineering Internship  
**Assignment:** Prompt Iteration Log and Cross-Model Comparison (FL-02)  
**Selected Target Task from FL-01:** Target Task 01: Develop one NEXI Network PWA feature  

---

## 1. Selected Task and Audit Context

### Task Description
- **Target Task:** Develop one NEXI Network PWA feature: Member Event QR Code Check-in and Attendance Verification API.
- **Context:** NEXI Network is the student IT organization of STI College San Pablo. During tech summits and workshops, student attendees check into sessions using mobile phones over congested campus Wi-Fi. Organization officers scan attendee QR codes to log attendance.
- **Definition of "Done Well" (from FL-01 Audit):**
  1. Start with a clear problem statement and written acceptance criteria.
  2. Complete the full intended user flow (scan QR, verify event, record timestamp, return confirmation).
  3. Pass at least five test cases, including an error state (invalid QR) and an empty or duplicate state.
  4. Ensure zero critical console errors, no exposed secrets, and handle spotty network connectivity idempotently.
  5. Explain the feature workflow, key technical decisions, and database behavior in plain words.
  6. Enable another NEXI officer to test and verify the feature successfully without assistance.

---

## 2. Iteration Summary Table

| Rung | Version | Named Technique Applied | Primary Output Change | Status |
| :--- | :--- | :--- | :--- | :--- |
| **0** | **Naive Version** | *None (Raw Prompt)* | Generic, unstructured Node/Express toy script with hardcoded arrays and zero validation | Baseline |
| **1** | **Version 1** | **Role Assignment** | Shifted tone to senior engineering mentor; focused on PWA concerns, but stack was still assumed | Improved |
| **2** | **Version 2** | **Context and Motivation** | Switched stack to Python/FastAPI; addressed campus Wi-Fi drops and duplicate scan risks | Improved |
| **3** | **Version 3** | **Few-Shot Examples** | Locked down request and response JSON schemas; model stopped guessing payload fields | Improved |
| **4** | **Version 4** | **Output Structure** | Partitioned output into 4 discrete deliverables matching FL-01 audit criteria | Improved |
| **5** | **Version 5** | **Step Decomposition** | Enforced step-by-step reasoning; introduced atomic database constraints and race condition guards | Production-Ready |

---

## 3. The Prompt Iteration Ladder

### Run 0: Naive Version (Baseline)

#### Prompt
```text
Help me code an attendance check-in feature for our student org web app.
```

#### Representative Output Excerpt
```javascript
// Here is a simple Express.js check-in endpoint for your student org app!
const express = require('express');
const app = express();
app.use(express.json());

let attendanceList = [];

app.post('/checkin', (req, res) => {
    const { studentName, eventId } = req.body;
    
    if (!studentName || !eventId) {
        return res.status(400).send("Please provide student name and event ID!");
    }
    
    attendanceList.push({
        name: studentName,
        event: eventId,
        date: new Date()
    });
    
    console.log(`Checked in: ${studentName}`);
    return res.status(200).json({ message: "Check-in successful!", total: attendanceList.length });
});

app.listen(3000, () => console.log("Server running on port 3000"));
```

#### Evaluation Note
- **What changed in prompt:** Baseline prompt: raw, one-line request typed before starting this track.
- **Observed output difference:** The model guessed everything. It assumed Node.js/Express, used a volatile in-memory array (`let attendanceList = []`), relied on student names instead of verified student IDs or QR hashes, accepted duplicate check-ins without restriction, and provided zero automated tests.
- **Why it failed:** Lacked role context, technical constraints, organization background, and explicit deliverables.

---

### Run 1: Version 1 (Technique: Role Assignment)

#### Prompt
```text
You are a Staff Full-Stack Software Engineer who specializes in Progressive Web Apps (PWAs) and secure event management backends.

Help me code an attendance check-in feature for our student org web app.
```

#### Representative Output Excerpt
```text
As a Staff Engineer designing for PWAs, event check-in systems require high reliability, offline resilience, and defense against duplicate records.

Here is an architectural overview and backend prototype:
1. PWA Service Worker caching strategy for offline QR queueing.
2. Token-based verification to ensure QR codes are signed and cannot be forged.
3. RESTful API route with database persistence.

[Code omitted: 90 lines of mixed Node.js and client-side IndexedDB code]
```

#### Evaluation Note
- **What changed in prompt:** Added **Role Assignment** ("Staff Full-Stack Software Engineer specializing in PWAs and secure event management backends").
- **Observed output difference:** The model stopped writing naive beginner code and adopted an architectural engineering persona. It immediately flagged offline queueing and QR forgery risks.
- **Why it failed:** Because the framework and organization environment were not specified, the model attempted to solve both frontend IndexedDB caching and backend routing in one response, spreading itself too thin.

---

### Run 2: Version 2 (Technique: Context and Motivation)

#### Prompt
```text
You are a Staff Full-Stack Software Engineer who specializes in Progressive Web Apps (PWAs) and secure event management backends.

Context and Motivation:
This feature is for NEXI Network, an IT student organization at STI College San Pablo. During tech events, student attendees check into sessions by presenting a dynamic QR code on their phone, which is scanned by student officers. The campus venue has congested, intermittent Wi-Fi, which previously caused duplicate check-in submissions, stalled queues, and database lockups. We are building this on a Python 3.11 and FastAPI backend with PostgreSQL.

Task:
Build the backend check-in verification API endpoint that handles attendance recording reliably and prevents duplicate scans.
```

#### Representative Output Excerpt
```python
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional
import asyncpg

app = FastAPI()

class CheckInRequest(BaseModel):
    student_id: str = Field(..., example="02000123456")
    event_id: str = Field(..., example="nexi-summit-2026")
    qr_token: str = Field(..., example="signed-qr-hash-xyz")
    scanned_by_officer_id: str = Field(..., example="officer-01")

@app.post("/api/v1/attendance/checkin", status_code=status.HTTP_200_OK)
async def record_checkin(payload: CheckInRequest):
    # Check if student already checked in to prevent duplicates
    query_existing = "SELECT id, checked_in_at FROM attendance WHERE student_id = $1 AND event_id = $2"
    # ... executes query ...
    if existing:
        return {
            "status": "already_checked_in",
            "message": "Student is already checked in for this event.",
            "timestamp": existing["checked_in_at"]
        }
    
    insert_query = """
        INSERT INTO attendance (student_id, event_id, qr_token, scanned_by, checked_in_at)
        VALUES ($1, $2, $3, $4, NOW())
        RETURNING id, checked_in_at;
    """
    # ... executes insert ...
    return {"status": "success", "message": "Attendance confirmed."}
```

#### Evaluation Note
- **What changed in prompt:** Added **Context and Motivation** detailing NEXI Network, campus Wi-Fi congestion, past duplicate scan pain points, and the required Python/FastAPI/PostgreSQL stack.
- **Observed output difference:** The model completely abandoned JavaScript, switched to Python/FastAPI, adopted realistic student ID conventions, and designed duplicate scan checks specifically addressing the slow Wi-Fi problem.
- **Why it failed:** The JSON response payload was still ambiguous (it returned HTTP 200 OK for already-checked-in records instead of HTTP 409 Conflict), and it lacked test cases to satisfy FL-01 audit criteria.

---

### Run 3: Version 3 (Technique: Few-Shot Examples)

#### Prompt
```text
You are a Staff Full-Stack Software Engineer who specializes in Progressive Web Apps (PWAs) and secure event management backends.

Context and Motivation:
This feature is for NEXI Network, an IT student organization at STI College San Pablo. During tech events, student attendees check into sessions by presenting a QR code on their phone, which is scanned by student officers. The venue has congested Wi-Fi, which previously caused duplicate submissions. We are building this on a Python 3.11 and FastAPI backend with PostgreSQL.

Few-Shot Examples of Expected API Behavior:

Example 1: First-time successful check-in
Request: POST /api/v1/attendance/checkin
Body: {"event_id": "nexi-2026-summit", "student_id": "02000234567", "qr_signature": "valid-sig-123"}
Response: HTTP 200 OK
Body: {"status": "verified", "student_id": "02000234567", "event_id": "nexi-2026-summit", "checked_in_at": "2026-09-28T09:30:00Z", "is_duplicate": false}

Example 2: Duplicate scan attempt (e.g. officer double-taps button or network retry)
Request: POST /api/v1/attendance/checkin (same payload within same event)
Response: HTTP 409 Conflict
Body: {"status": "conflict", "error_code": "DUPLICATE_CHECKIN", "message": "Student already checked in at 09:30:00Z", "original_timestamp": "2026-09-28T09:30:00Z"}

Example 3: Invalid or inactive event
Request: POST /api/v1/attendance/checkin
Body: {"event_id": "non-existent-event", "student_id": "02000234567", "qr_signature": "sig"}
Response: HTTP 404 Not Found
Body: {"status": "not_found", "error_code": "EVENT_NOT_ACTIVE", "message": "Event is not active or does not exist."}

Task:
Build the FastAPI attendance verification endpoint that matches the exact behavior demonstrated in the examples above.
```

#### Representative Output Excerpt
```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/attendance", tags=["Attendance"])

class CheckInPayload(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    student_id: str = Field(..., description="Student ID number")
    qr_signature: str = Field(..., description="Cryptographic signature from QR code")

@router.post("/checkin", status_code=status.HTTP_200_OK)
async def checkin(payload: CheckInPayload):
    # Matches Example 3
    event = await get_event(payload.event_id)
    if not event or not event.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "not_found",
                "error_code": "EVENT_NOT_ACTIVE",
                "message": "Event is not active or does not exist."
            }
        )

    # Matches Example 2
    existing_record = await get_attendance(payload.event_id, payload.student_id)
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "status": "conflict",
                "error_code": "DUPLICATE_CHECKIN",
                "message": f"Student already checked in at {existing_record.checked_in_at.strftime('%H:%M:%SZ')}",
                "original_timestamp": existing_record.checked_in_at.isoformat()
            }
        )

    # Matches Example 1
    new_record = await record_attendance(payload.event_id, payload.student_id, payload.qr_signature)
    return {
        "status": "verified",
        "student_id": new_record.student_id,
        "event_id": new_record.event_id,
        "checked_in_at": new_record.checked_in_at.isoformat(),
        "is_duplicate": False
    }
```

#### Evaluation Note
- **What changed in prompt:** Added **Few-Shot Examples** illustrating exact HTTP requests, status codes (200, 409, 404), and error body contracts.
- **Observed output difference:** The model stopped inventing inconsistent responses; it implemented HTTP 409 Conflict instead of returning 200 for duplicates, and mirrored the structured error dictionaries shown in the examples.
- **Why it failed:** The output was just raw code with placeholder helper functions (`get_event`, `record_attendance`). It did not provide the test cases, database model, or officer testing guide required by the FL-01 definition of done well.

---

### Run 4: Version 4 (Technique: Output Structure)

#### Prompt
```text
You are a Staff Full-Stack Software Engineer who specializes in Progressive Web Apps (PWAs) and secure event management backends.

Context and Motivation:
This feature is for NEXI Network, an IT student organization at STI College San Pablo. During tech events, student attendees check into sessions by presenting a QR code on their phone, which is scanned by student officers. The venue has congested Wi-Fi, which previously caused duplicate submissions. We are building this on a Python 3.11 and FastAPI backend with PostgreSQL.

Few-Shot Examples of Expected API Behavior:
[Included the 3 examples from Version 3]

Output Structure:
Format your entire response strictly into four labeled Markdown sections:
### Section 1: Architecture and Database Model
- Table definition with unique constraints to ensure idempotency at the database level.
### Section 2: Complete FastAPI Endpoint Implementation
- Copy-pasteable code with Pydantic validation, database session injection, and custom HTTPExceptions.
### Section 3: Five Comprehensive Test Cases
- Must include: (1) Valid first-time check-in, (2) Duplicate scan within same session, (3) Non-existent event, (4) Tampered/empty QR signature, and (5) Concurrency race-condition test.
### Section 4: NEXI Officer Hand-off Guide
- Plain-English instructions so another student officer can test and verify this endpoint without developer intervention.
```

#### Representative Output Excerpt
```text
### Section 1: Architecture and Database Model
We enforce a unique composite constraint on (event_id, student_id) in PostgreSQL so duplicate inserts are rejected by the database engine even if simultaneous requests slip past application checks.

[SQLAlchemy 2.0 User model shown with UniqueConstraint('event_id', 'student_id')]

### Section 2: Complete FastAPI Endpoint Implementation
[Complete router code with async SQLAlchemy session]

### Section 3: Five Comprehensive Test Cases
1. test_valid_first_time_checkin -> Expect 200 OK
2. test_duplicate_checkin_returns_409 -> Expect 409 Conflict
3. test_inactive_event_returns_404 -> Expect 404 Not Found
4. test_empty_qr_signature_returns_422 -> Expect 422 Unprocessable Entity
5. test_concurrent_double_scan_atomic -> Expect exactly one 200 and one 409

### Section 4: NEXI Officer Hand-off Guide
To verify this feature:
1. Open the Swagger docs at http://localhost:8000/docs.
2. Expand POST /api/v1/attendance/checkin.
3. Click "Try it out" and test with valid student ID...
```

#### Evaluation Note
- **What changed in prompt:** Added **Output Structure** mandating four explicit sections matching the FL-01 audit criteria: Architecture, Code, 5 Test Cases, and Officer Hand-off.
- **Observed output difference:** The unstructured code dump transformed into a comprehensive engineering deliverable. The model explicitly included the unique composite constraint and wrote out all 5 test case descriptions.
- **Why it failed:** The implementation in Section 2 still used a naive `SELECT then INSERT` approach in Python rather than an atomic `INSERT ... ON CONFLICT DO NOTHING` statement. Under rapid scanning, two simultaneous requests could both pass the `SELECT` query before either committed.

---

### Run 5: Version 5 (Technique: Step Decomposition) - The Final Refinement

#### Prompt
```text
You are a Staff Full-Stack Software Engineer who specializes in Progressive Web Apps (PWAs) and secure event management backends.

Context and Motivation:
This feature is for NEXI Network, an IT student organization at STI College San Pablo. During tech events, student attendees check into sessions by presenting a QR code on their phone, which is scanned by student officers. The venue has congested Wi-Fi, which previously caused duplicate submissions. We are building this on a Python 3.11 and FastAPI backend with PostgreSQL.

Few-Shot Examples of Expected API Behavior:
[Included the 3 examples from Version 3]

Output Structure:
Format your entire response strictly into four labeled Markdown sections:
### Section 1: Architecture and Database Model
### Section 2: Complete FastAPI Endpoint Implementation
### Section 3: Five Comprehensive Test Cases
### Section 4: NEXI Officer Hand-off Guide

Step Decomposition Instructions:
Think step-by-step through the implementation before writing code:
1. Step 1 (Concurrency & Idempotency): Analyze the race condition where spotty Wi-Fi causes a browser to retry twice within 100ms. Explain how PostgreSQL unique constraints handle this atomically.
2. Step 2 (Validation & Security): Inspect payload fields with Pydantic v2. Check for empty strings, malicious characters, and signature validity before issuing database queries.
3. Step 3 (FastAPI Router Construction): Write clean, production-ready code with AsyncSession. Handle IntegrityError cleanly to return HTTP 409 Conflict without leaking raw SQL errors.
4. Step 4 (Pytest Suite): Write actual executable pytest functions using httpx.AsyncClient covering all 5 test scenarios.
5. Step 5 (Officer Verification Manual): Write step-by-step testing instructions with curl commands that any non-technical student officer can copy and run.
```

#### Representative Output Excerpt
```python
# From Section 2: Complete FastAPI Endpoint Implementation
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.models.attendance import AttendanceRecord
from app.schemas.attendance import CheckInPayload, CheckInResponse

router = APIRouter(prefix="/api/v1/attendance", tags=["NEXI Attendance"])

@router.post(
    "/checkin",
    response_model=CheckInResponse,
    status_code=status.HTTP_200_OK,
    summary="Record event check-in idempotently"
)
async def checkin_attendee(payload: CheckInPayload, db: AsyncSession = Depends(get_db)):
    # 1. Verify Event exists and is currently accepting check-ins
    event = await db.get(EventModel, payload.event_id)
    if not event or not event.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"status": "not_found", "error_code": "EVENT_NOT_ACTIVE", "message": "Event is not active."}
        )

    # 2. Check for existing record to provide clear timestamp info
    existing = await db.scalar(
        select(AttendanceRecord).where(
            AttendanceRecord.event_id == payload.event_id,
            AttendanceRecord.student_id == payload.student_id
        )
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "status": "conflict",
                "error_code": "DUPLICATE_CHECKIN",
                "message": f"Student already checked in at {existing.checked_in_at.strftime('%H:%M:%SZ')}",
                "original_timestamp": existing.checked_in_at.isoformat()
            }
        )

    # 3. Insert new attendance record inside a transaction catching IntegrityError
    new_record = AttendanceRecord(
        event_id=payload.event_id,
        student_id=payload.student_id,
        qr_signature=payload.qr_signature,
        scanned_by=payload.scanned_by
    )
    db.add(new_record)
    try:
        await db.commit()
        await db.refresh(new_record)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"status": "conflict", "error_code": "CONCURRENT_SCAN", "message": "Check-in collision detected."}
        )

    return CheckInResponse(
        status="verified",
        student_id=new_record.student_id,
        event_id=new_record.event_id,
        checked_in_at=new_record.checked_in_at,
        is_duplicate=False
    )
```

#### Evaluation Note
- **What changed in prompt:** Added **Step Decomposition** requiring the model to reason through concurrency, validation, error mapping, testing, and officer hand-off in sequence.
- **Observed output difference:** The code achieved true production robustness. It wrapped database commits in a `try...except IntegrityError` block with rollback, preventing raw database crashes during concurrent double-scans. The pytest suite was no longer descriptive bullet points: it wrote executable `httpx.AsyncClient` tests with mocked dependencies.
- **Result:** Fully met all six "Done Well" criteria from the FL-01 audit.

---

## 4. Cross-Model Comparison: Claude vs. ChatGPT

The final engineered prompt (Version 5) was executed on both **Claude 3.5 Sonnet** and **ChatGPT (GPT-4o)** using identical parameters. Below is a side-by-side comparative analysis across four evaluation dimensions:

### 1. Tone and Persona
- **Claude 3.5 Sonnet:**
  - Adopted a concise, highly pragmatic staff engineer persona.
  - Omitted conversational filler, introductory pleasantries, and cheerleading.
  - Wrote developer docstrings focusing on failure modes, database indexing decisions, and boundary edge cases.
- **ChatGPT (GPT-4o):**
  - Adopted an encouraging, instructional tone ("Great feature for NEXI Network! Here is your complete implementation:").
  - Included helpful but unasked-for extras, such as explaining how to run Docker compose and suggesting frontend QR-scanner libraries for React/Vue.
- **Verdict on Tone:** Claude's tone was more aligned with a professional production codebase; ChatGPT felt more like an interactive coding bootcamp instructor.

### 2. Technical Accuracy and Robustness
- **Claude 3.5 Sonnet:**
  - Correctly recognized the specific concurrency risk of network retries under spotty Wi-Fi.
  - Implemented an explicit `UniqueConstraint("event_id", "student_id", name="uq_event_student")` at the SQLAlchemy table level AND handled `sqlalchemy.exc.IntegrityError` with clean session rollback.
  - Handled UTC timestamps correctly using `datetime.now(timezone.utc)`.
- **ChatGPT (GPT-4o):**
  - Included a unique constraint in the model, but in the route handler, it relied primarily on `if existing: return 409` before the insert.
  - In its first code iteration, it omitted the `try...except IntegrityError` wrapper around `await db.commit()`, which would have caused an unhandled 500 Internal Server Error if two scans resolved at the exact same millisecond.
- **Verdict on Accuracy:** Claude demonstrated superior defensive backend rigor regarding race conditions and transaction rollbacks.

### 3. Structural Adherence
- **Claude 3.5 Sonnet:**
  - Strictly respected the 4 requested Markdown sections in exact sequence without merging or reordering.
  - Wrote executable `pytest` code in Section 3 and clean `curl` snippets in Section 4.
- **ChatGPT (GPT-4o):**
  - Respected the 4 sections, but inserted sub-sections (e.g., "Prerequisites", "Environment Setup", "Next Steps") that lengthened the response and diluted the hand-off manual.
- **Verdict on Structure:** Claude adhered more strictly to negative structural constraints; ChatGPT expanded the scope.

### 4. Failure Points and Over-Engineering
- **Claude 3.5 Sonnet Failure Point:**
  - Claude assumed an existing `get_db` dependency and database configuration file (`app.db.session`), leaving imports as external assumptions without providing the minimal 5-line engine setup. A junior developer would have to manually create the engine file.
- **ChatGPT (GPT-4o) Failure Point:**
  - ChatGPT over-engineered the QR signature verification by hallucinating an HMAC secret-signing utility that was not specified in the prompt, adding unnecessary complexity to what was intended to be an attendance recording endpoint.
- **Verdict on Failure Points:** Claude under-specified database setup plumbing; ChatGPT over-engineered cryptographic utilities.

---

## 5. Final Reusable Prompt Template

The prompt below is distilled so that any developer, student officer, or intern can take it and generate a robust, production-ready feature implementation for any web application without requiring personal context.

```markdown
You are a Staff Full-Stack Software Engineer specializing in Progressive Web Apps (PWAs) and resilient backend service design.

### Context and Operational Goal
Feature Target: [FEATURE_NAME] for [ORGANIZATION_NAME / APPLICATION_NAME].
Operating Environment: [USER_ENVIRONMENT_AND_CONSTRAINTS, e.g., mobile users on congested campus Wi-Fi, low-bandwidth conditions, or intermittent connectivity].
Primary Technical Risk: [PRIMARY_RISK, e.g., duplicate submissions, race conditions during rapid actions, or data loss during disconnects].
Technology Stack: [TECH_STACK, e.g., Python 3.11, FastAPI, SQLAlchemy 2.0 async, PostgreSQL].

### Few-Shot Expected Behavior
- Case 1 (Standard Success):
  Request: [METHOD] [ENDPOINT] with [SAMPLE_VALID_PAYLOAD]
  Response: HTTP [SUCCESS_STATUS_CODE] with [SAMPLE_SUCCESS_JSON]
- Case 2 (Duplicate / Conflict State):
  Request: Repeated [METHOD] [ENDPOINT] with identical key fields
  Response: HTTP [CONFLICT_STATUS_CODE] with [SAMPLE_CONFLICT_JSON]
- Case 3 (Missing / Invalid Dependency):
  Request: [METHOD] [ENDPOINT] targeting invalid resource
  Response: HTTP [ERROR_STATUS_CODE] with [SAMPLE_ERROR_JSON]

### Step Decomposition Instructions
Reason through the solution sequentially before writing code:
1. Data Integrity: Design the schema with database-level unique constraints to guarantee idempotency under concurrent retries.
2. Validation: Define strict Pydantic v2 schemas validating all payload inputs before database interaction.
3. Route Implementation: Write clean, copy-pasteable endpoint code. Catch database integrity collisions and return descriptive HTTP status codes.
4. Testing: Write 5 automated test functions using an async test client covering: (1) Happy path, (2) Duplicate submission, (3) Invalid resource, (4) Empty/malformed input, (5) Concurrent submission collision.
5. Non-Technical Hand-Off: Provide step-by-step verification instructions using curl that a non-engineer can execute.

### Required Output Format
Structure your response strictly into these labeled sections:
### Section 1: Architecture and Database Model
### Section 2: Complete Endpoint Implementation
### Section 3: Five Executable Test Cases
### Section 4: Non-Technical Verification Guide
```

---

## 6. Key Takeaways and Personal Reflection

1. **Prompts Are Specifications:** A prompt is not a search query; it is a software requirements specification (SRS). The baseline prompt produced toy code because it specified nothing. When role, context, examples, structure, and step-by-step reasoning were added, the LLM performed at a staff engineer level.
2. **Few-Shot Examples Prevent Schema Hallucination:** Adding three small examples of exact JSON payloads and status codes eliminated 90% of model ambiguity regarding API contracts.
3. **Claude vs. ChatGPT Specialties:** Claude 3.5 Sonnet excels at architectural precision, defensive transaction rollbacks, and adherence to negative constraints. ChatGPT (GPT-4o) excels at educational explanations, end-to-end scaffolding, and developer onboarding tutorials.
