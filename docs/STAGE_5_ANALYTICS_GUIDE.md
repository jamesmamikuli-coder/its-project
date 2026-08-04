# 📊 Stage 5 — Analytics Dashboard Backend
# Setup Guide (Windows)

---

## What Was Built in Stage 5

| File | Status | What it does |
|------|--------|--------------|
| `services/analytics_engine.py` | NEW | All analytics computations |
| `routes/analytics_routes.py` | UPDATED | 4 real dashboard endpoints |
| `test_analytics.py` | NEW | 10 automated tests |

---

## What Each Dashboard Shows

### Student Dashboard  →  GET /api/analytics/student/me

The student sees a complete picture of their own learning:

```
┌────────────────────────────────────────────────────┐
│  SUMMARY CARDS                                     │
│  Quizzes: 12 │ Avg Score: 68.5% │ Time: 24 mins   │
└────────────────────────────────────────────────────┘
┌───────────────────┐  ┌─────────────────────────────┐
│  TOPIC BREAKDOWN  │  │  SCORE OVER TIME             │
│  (bar chart)      │  │  (line chart)                │
│  Algorithms: 55%  │  │  Q1:60% Q2:80% Q3:70%...    │
│  Databases:  85%  │  └─────────────────────────────┘
│  OOP:        72%  │
└───────────────────┘
┌───────────────────┐  ┌─────────────────────────────┐
│  WEAKEST TOPIC    │  │  DIFFICULTY DISTRIBUTION     │
│  ⚠ Algorithms    │  │  Easy:5  Medium:5  Hard:2    │
│  Focus here next! │  └─────────────────────────────┘
└───────────────────┘
┌────────────────────────────────────────────────────┐
│  CHATBOT STATS                                     │
│  Questions asked: 8 │ Helpful: 5 │ Not helpful: 1 │
└────────────────────────────────────────────────────┘
```

### Instructor Dashboard  →  GET /api/analytics/instructor

The instructor sees the whole class at once:

```
┌──────────────────────────────────────────────────────┐
│  CLASS SUMMARY                                       │
│  Students: 25 │ Quizzes: 143 │ Class Avg: 68.4%     │
│  At Risk: 4   │ Top Performers: 7                   │
└──────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────┐
│  AT-RISK STUDENTS (avg < 50%, 2+ quizzes)            │
│  🔴 Ibrahim Musa     — 28.0%  (5 quizzes)           │
│  🔴 Chiamaka Obi     — 35.0%  (3 quizzes)           │
└──────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────┐
│  STUDENT TABLE (all students with their stats)       │
│  Name         │ Avg  │ Quizzes │ Chatbot │ At Risk  │
│  Amina Bello  │ 92%  │   8     │    3    │ No       │
│  Kwame Osei   │ 87%  │   6     │    1    │ No       │
│  ...                                                 │
└──────────────────────────────────────────────────────┘
┌─────────────────────────┐  ┌──────────────────────────┐
│  CLASS TOPIC BREAKDOWN  │  │  CHATBOT ANALYTICS       │
│  Algorithms:  58%       │  │  Total questions: 47     │
│  Data Struct: 71%       │  │  Helpful rate:   68%     │
│  Databases:   83%       │  │  Top topic: Data Struct  │
└─────────────────────────┘  └──────────────────────────┘
```

---

## Step-by-Step Setup

### Step 1 — Extract ZIP and open in VS Code

Download `ITS_Project_Stage5.zip`, extract it, open in VS Code.

New files to check for:
```
backend/
├── test_analytics.py               ← NEW
├── services/
│   └── analytics_engine.py         ← NEW
└── routes/
    └── analytics_routes.py         ← UPDATED (real endpoints now)
```

---

### Step 2 — Start the server

```
cd backend
venv\Scripts\activate
python app.py
```

---

### Step 3 — Run all tests (including Stage 5)

```
cd backend
venv\Scripts\activate
python test_analytics.py
```

Expected output:
```
=====================================================
  TEST 1: Student gets own dashboard
=====================================================
  ✅ PASS  Status code is 200
  ✅ PASS  Has 'summary' section
  ✅ PASS  Has 'topic_breakdown' section
  ...
=====================================================
  RESULTS: 10/10 tests passed
  🎉 All tests passed! Analytics engine working correctly.
=====================================================
```

---

## All Analytics Endpoints

| Method | URL | Who | What it does |
|--------|-----|-----|--------------|
| GET | /api/analytics/student/me | Student | My full dashboard |
| GET | /api/analytics/instructor | Instructor | Class-wide overview |
| GET | /api/analytics/student/\<id\> | Instructor | One student's data |
| GET | /api/analytics/leaderboard | Both | Top 10 students |

---

## Manual Testing with Thunder Client

### Test 1: My student dashboard

- Method: GET
- URL: `http://localhost:5000/api/analytics/student/me`
- Header: `Authorization: Bearer <student token>`

You need to have completed at least one quiz first.
If the `topic_breakdown` list is empty, start and submit a quiz.

---

### Test 2: Instructor class overview

- Method: GET
- URL: `http://localhost:5000/api/analytics/instructor`
- Header: `Authorization: Bearer <instructor token>`

---

### Test 3: One student's detail (instructor only)

- Method: GET
- URL: `http://localhost:5000/api/analytics/student/1`
  (replace 1 with a real student ID from the users list)
- Header: `Authorization: Bearer <instructor token>`

---

### Test 4: Leaderboard

- Method: GET
- URL: `http://localhost:5000/api/analytics/leaderboard`
- Header: `Authorization: Bearer <any token>`

Note: students only appear on the leaderboard after completing
at least 2 quizzes.

---

## Understanding At-Risk Detection

A student is flagged as "at risk" when ALL of these are true:

1. They have completed **2 or more quizzes** (enough data to judge)
2. Their average score is **below 50%**

The instructor dashboard shows at-risk students sorted by worst
score first — so the most urgent cases are at the top.

---

## Understanding the Leaderboard

Only students with **2 or more completed quizzes** appear on the
leaderboard. This is intentional — a student who scored 100% on
one quiz shouldn't top the leaderboard before others with more
evidence of performance.

Badges awarded:
- 🏆 First place
- 🥈 Second place
- 🥉 Third place
- ⭐ All other positions

---

## Common Errors and Fixes

| Error | What it means | Fix |
|-------|---------------|-----|
| `topic_breakdown` is empty `[]` | No completed quizzes yet | Complete at least 1 quiz |
| `score_over_time` is empty `[]` | No completed quizzes | Complete at least 1 quiz |
| `leaderboard` is empty | No student has 2+ quizzes | Complete 2+ quizzes |
| `401 Unauthorized` | No token | Add Authorization header |
| `403 Forbidden` | Wrong role | Use instructor token for /instructor |

---

## Running All Four Test Suites Together

You can run all tests in sequence to verify the whole backend:

```
cd backend
venv\Scripts\activate

python test_auth.py
python test_qa.py
python test_quiz.py
python test_analytics.py
```

A fully working Stage 5 backend should show:
```
test_auth.py      → 10/10 passed
test_qa.py        → 10/10 passed
test_quiz.py      → 10/10 passed
test_analytics.py → 10/10 passed
```

---

## Stage 5 Checklist

- [ ] `python app.py` starts without errors
- [ ] `python test_analytics.py` shows 10/10 tests passing
- [ ] Complete 2+ quizzes with the student account
- [ ] Thunder Client: GET /analytics/student/me → see topic_breakdown populated
- [ ] Thunder Client: GET /analytics/instructor → see student table and at-risk list
- [ ] Thunder Client: GET /analytics/leaderboard → see ranked students
- [ ] Thunder Client: Student tries GET /analytics/instructor → gets 403
- [ ] Thunder Client: GET /analytics/student/999999 → gets 404

---

## Backend Is Now Complete! 🎉

All five backend stages are done:

| Stage | What was built | Status |
|-------|---------------|--------|
| 1 | Project setup, database schema, placeholder routes | ✅ |
| 2 | Authentication, JWT, role-based access, db helpers | ✅ |
| 3 | NLP Q&A chatbot engine (TF-IDF search) | ✅ |
| 4 | Adaptive quiz engine (difficulty algorithm) | ✅ |
| 5 | Analytics dashboard (student + instructor) | ✅ |

The entire Flask API is working. Reply **"Start Stage 6"** and we will
build the **React frontend** — the complete web interface with login,
student dashboard, Q&A chatbot, quiz page, and analytics charts! ⚛️
