# 🔐 Stage 2 — Authentication System Guide

This guide explains every new file added in Stage 2 and walks you through
adding them to your project, running the tests, and understanding what
was built and why.

---

## What Was Added in Stage 2

Stage 1 gave you the skeleton. Stage 2 adds the security layer —
the system that controls WHO can log in and WHAT they're allowed to do.

| File | New or Updated | What it does |
|------|---------------|--------------|
| `middleware/auth_middleware.py` | NEW | Route guards — checks tokens and roles |
| `services/db_service.py` | NEW | Reusable database query helpers |
| `routes/auth_routes.py` | UPDATED | Full 8-endpoint auth system |
| `test_auth.py` | NEW | Automated test script (10 tests) |

---

## How to Add the New Files to Your Project

### Step 1 — Extract the ZIP

Download and extract `ITS_Project_Stage2.zip`. You will get the full
`ITS_Project` folder with all the new files already in place.

### Step 2 — Copy files into your existing project

If you already have a Stage 1 folder on your laptop, copy these files
from the ZIP into the matching locations:

```
From ZIP:                                  → Copy to your project:
backend/middleware/auth_middleware.py      → backend/middleware/auth_middleware.py
backend/services/db_service.py            → backend/services/db_service.py
backend/routes/auth_routes.py             → backend/routes/auth_routes.py  (REPLACE)
backend/test_auth.py                      → backend/test_auth.py
```

NOTE: `auth_routes.py` is a full replacement of the Stage 1 version.
The models, app.py, config, and seed files do NOT change in Stage 2.

### Step 3 — Install the requests library for testing

The test script uses a library called `requests` to make HTTP calls.
Install it with your virtual environment active:

```
venv\Scripts\activate
pip install requests
```

---

## Understanding the New Files

### middleware/auth_middleware.py — The Security Guards

This file contains three "decorators". A decorator is a function that
wraps around a route function and runs BEFORE it. Think of it as a
security guard standing at the door of a room.

```
Request comes in
       │
       ▼
  @login_required  ← Guard checks: is there a valid token?
       │                NO → return 401 Unauthorized immediately
       │                YES → continue
       ▼
  Route function runs  ← Only reached if guard passed
```

The three guards:

```python
@login_required       # Any logged-in user passes (student or instructor)
@student_required     # Only users with role="student" pass
@instructor_required  # Only users with role="instructor" pass
```

**Example in use:**

```python
@quiz_bp.route("/start")
@student_required          # Guard runs first
def start_quiz():
    user = get_current_user()   # Get the logged-in user
    ...
```

If a student token is sent → quiz starts.
If an instructor token is sent → 403 Forbidden.
If no token is sent → 401 Unauthorized.

---

### services/db_service.py — The Database Helper Library

Instead of writing the same database queries in multiple route files,
we write them once here. Any file can import and use them.

Two classes are provided:

**UserService** — queries about users:

```python
from services.db_service import UserService

user    = UserService.get_by_id(5)
student = UserService.get_by_email("amina@example.com")
summary = UserService.get_student_summary(user_id=5)
# Returns: { total_quizzes, average_score, is_at_risk, ... }

overview = UserService.get_class_overview()
# Returns: { total_students, class_average, at_risk_students, ... }
```

**QuizService** — queries about quizzes and adaptive difficulty:

```python
from services.db_service import QuizService

topics  = QuizService.get_all_topics()
# Returns: ["Data Structures", "Algorithms", ...]

level   = QuizService.determine_difficulty(user_id=5, topic="Algorithms")
# Returns: 1 (Easy), 2 (Medium), or 3 (Hard)
# This is the ADAPTIVE algorithm — reads recent scores and decides!

scores  = QuizService.get_student_topic_scores(user_id=5)
# Returns: { "Algorithms": { "average_score": 72.5, "attempts": 3 }, ... }

history = QuizService.get_score_history(user_id=5)
# Returns: [ { "date": "2025-01-10", "score": 65.0, ... }, ... ]
```

---

### routes/auth_routes.py — All 8 Auth Endpoints

| Method | URL | Who | What happens |
|--------|-----|-----|--------------|
| POST | `/api/auth/register` | Anyone | Creates account, returns token |
| POST | `/api/auth/login` | Anyone | Verifies password, returns token |
| GET | `/api/auth/me` | Logged in | Returns your profile |
| PUT | `/api/auth/me` | Logged in | Updates your name or email |
| PUT | `/api/auth/change-password` | Logged in | Changes password (needs old one) |
| GET | `/api/auth/users` | Instructor | Lists all users, supports filtering |
| GET | `/api/auth/users/<id>` | Instructor | Gets one user's profile |
| DELETE | `/api/auth/users/<id>` | Instructor | Deletes a user account |

---

## Understanding JWT Tokens

After you register or log in, the server returns a token like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.abc123xyz...
```

This token is like a wristband at an event — show it at the door to
get in. The frontend stores this token and sends it with every request
that requires authentication in the HTTP header:

```
Authorization: Bearer eyJhbGciOiJIUzI1Ni...
```

The server reads that header, verifies the token is valid (not expired,
not tampered with), extracts the user ID stored inside it, and loads
that user from the database — all automatically via the @login_required
decorator.

Tokens expire after 24 hours (set in config/settings.py). After that,
the user must log in again to get a fresh token.

---

## Running the Tests

### Step 1 — Start the Flask server (Terminal 1)

```
cd backend
venv\Scripts\activate
python app.py
```

Leave this running. You should see:
```
✅ Database tables created / verified.
🚀 ITS Backend server starting on http://localhost:5000
```

### Step 2 — Run the tests (Terminal 2)

Open a second terminal in VS Code by clicking the + button in the
terminal panel. Then:

```
cd backend
venv\Scripts\activate
python test_auth.py
```

### Expected output — all green:

```
====================================================
  TEST 1: Register a new student
====================================================
  PASS  Status 201 Created
  PASS  Has 'token'
  PASS  Has 'user'
  PASS  Role=student
  PASS  No password in response

... (more tests) ...

====================================================
  RESULTS: 10/10 tests passed
  All tests passed! Auth is working correctly.
====================================================
```

---

## Common Errors and Fixes

| Error | What it means | How to fix |
|-------|--------------|------------|
| `Connection refused` | Flask server isn't running | Run `python app.py` in Terminal 1 |
| `401 Unauthorized` | No token or invalid token | Include `Authorization: Bearer <token>` |
| `403 Forbidden` | Wrong role for this route | Your account role doesn't have permission |
| `409 Conflict` | Email already registered | Use a different email address |
| `400 Bad Request` | Missing or invalid fields | Check the `error` field in the response |
| `ModuleNotFoundError: requests` | Library not installed | Run `pip install requests` |

---

## ✅ Stage 2 Checklist

- [ ] All 4 new/updated files are in the correct locations
- [ ] `python app.py` starts without any errors
- [ ] `python test_auth.py` shows 10/10 tests passing
- [ ] Thunder Client: register a student → get back a token
- [ ] Thunder Client: register an instructor → get back a token
- [ ] Instructor token on `/api/auth/users` → 200 OK with list
- [ ] Student token on `/api/auth/users` → 403 Forbidden
- [ ] No token on `/api/auth/me` → 401 Unauthorized

---

## What Happens When You Run Everything Together

Here is the full flow of a student registering and then accessing a protected route:

```
Frontend sends:                     Backend does:
POST /api/auth/register
  { name, email, password }  →  1. Validates all fields
                                 2. Checks email not taken
                                 3. Hashes the password
                                 4. Saves User to database
                                 5. Creates JWT token
                              ←  Returns { token, user }

Frontend stores token.

GET /api/auth/me
  Authorization: Bearer token  →  1. @login_required reads header
                                   2. Verifies token is valid
                                   3. Loads User from database
                                   4. get_current_user() returns User
                                ←  Returns { user: { ... } }
```

---

## Ready for Stage 3?

Once your checklist is complete, reply **"Start Stage 3"** and we will
build the NLP Question Answering Engine — the chatbot that reads
student questions and finds the best answer from the knowledge base
using TF-IDF and cosine similarity. 🤖
