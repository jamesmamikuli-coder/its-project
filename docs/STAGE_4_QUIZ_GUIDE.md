# 📝 Stage 4 — Adaptive Quiz Engine
# Setup Guide (Windows)

---

## What Was Built in Stage 4

| File | Status | What it does |
|------|--------|--------------|
| `services/quiz_engine.py` | NEW | The adaptive quiz brain — difficulty selection, scoring |
| `routes/quiz_routes.py` | UPDATED | 5 real quiz endpoints (was a placeholder) |
| `test_quiz.py` | NEW | 10 automated tests for the quiz engine |

---

## How the Adaptive Engine Works (Plain English)

```
Student clicks "Start Quiz" on topic: Algorithms
                    │
                    ▼
      ┌─────────────────────────────────┐
      │  Look at last 3 quiz scores     │
      │  for this student + topic       │
      └─────────────────────────────────┘
                    │
          ┌─────────┴──────────┐
          │                    │
    No history           Has history
          │                    │
          ▼                    ▼
    Difficulty 1      Average < 50%  → Difficulty 1 (Easy)
      (Easy)          Average 50–79% → Difficulty 2 (Medium)
                      Average ≥ 80%  → Difficulty 3 (Hard)
                    │
                    ▼
      ┌─────────────────────────────────┐
      │  Pick 5 random questions at     │
      │  that difficulty level          │
      │  (different questions each time)│
      └─────────────────────────────────┘
                    │
                    ▼
      Send questions to student (NO correct answers shown)
                    │
                    ▼
      Student answers all 5, clicks Submit
                    │
                    ▼
      ┌─────────────────────────────────┐
      │  Score each answer              │
      │  Save all results to database   │
      │  Return: score, explanations,   │
      │  next difficulty recommendation │
      └─────────────────────────────────┘
```

---

## Step-by-Step Setup

### Step 1 — Extract the ZIP and open in VS Code

Download `ITS_Project_Stage4.zip`, extract it, and open the
`ITS_Project` folder in VS Code (File → Open Folder).

New files to check for:

```
ITS_Project/
└── backend/
    ├── test_quiz.py                    ← NEW FILE
    ├── services/
    │   └── quiz_engine.py              ← NEW FILE
    └── routes/
        └── quiz_routes.py              ← UPDATED (real endpoints)
```

---

### Step 2 — Activate venv and start the server

Press `Ctrl + backtick` to open the terminal, then:

```
cd backend
venv\Scripts\activate
python app.py
```

Expected startup output:
```
✅ Database tables created / verified.
🤖 QA Engine ready — 10 knowledge articles loaded.
🚀 ITS Backend server starting on http://localhost:5000
```

---

### Step 3 — Run the quiz tests

Open a second terminal tab (click `+` in the terminal panel), then:

```
cd backend
venv\Scripts\activate
python test_quiz.py
```

Expected output:
```
=====================================================
  TEST 1: Get available quiz topics
=====================================================
  ✅ PASS  Status code is 200
  ✅ PASS  Topics list is returned
  ✅ PASS  At least one topic exists
         Topics found: ['Algorithms', 'Data Structures', ...]
...
=====================================================
  RESULTS: 10/10 tests passed
  🎉 All tests passed! Quiz engine is working correctly.
=====================================================
```

---

## All Quiz Endpoints

| Method | URL | Who | What it does |
|--------|-----|-----|--------------|
| GET | /api/quiz/topics | Logged in | List all quiz topics |
| GET | /api/quiz/start?topic=X | Logged in | Start adaptive quiz |
| POST | /api/quiz/submit | Logged in | Submit answers, get score |
| GET | /api/quiz/history | Logged in | My past attempts |
| GET | /api/quiz/attempt/\<id\> | Logged in | Review one quiz |

---

## Manual Testing with Thunder Client

### Step 1 — Get topics

- Method: GET
- URL: `http://localhost:5000/api/quiz/topics`
- Header: `Authorization: Bearer <your token>`

Response:
```json
{
    "topics": ["Algorithms", "Data Structures", "Databases", "Programming Concepts"]
}
```

---

### Step 2 — Start a quiz

- Method: GET
- URL: `http://localhost:5000/api/quiz/start?topic=Algorithms`
- Header: `Authorization: Bearer <your token>`

Response:
```json
{
    "attempt_id": 1,
    "topic": "Algorithms",
    "difficulty": 1,
    "difficulty_label": "Easy",
    "total_questions": 5,
    "questions": [
        {
            "id": 4,
            "question_text": "What does Big O notation measure?",
            "option_a": "Memory usage",
            "option_b": "Algorithm efficiency",
            "option_c": "Code length",
            "option_d": "Number of bugs"
        },
        ...
    ]
}
```

Note: `correct_answer` is NOT in the response — students cannot cheat!

---

### Step 3 — Submit answers

Copy the `attempt_id` and each `id` from the questions above.

- Method: POST
- URL: `http://localhost:5000/api/quiz/submit`
- Header: `Authorization: Bearer <your token>`
- Body JSON:
```json
{
    "attempt_id": 1,
    "answers": [
        { "question_id": 4, "selected_answer": "B", "time_taken_secs": 12 },
        { "question_id": 7, "selected_answer": "A", "time_taken_secs": 8 },
        { "question_id": 2, "selected_answer": "C", "time_taken_secs": 15 },
        { "question_id": 9, "selected_answer": "D", "time_taken_secs": 10 },
        { "question_id": 5, "selected_answer": "B", "time_taken_secs": 7 }
    ]
}
```

Response includes:
- Your score as a percentage
- Whether each answer was correct
- The explanation for each question
- What difficulty level to expect NEXT time

---

### Step 4 — View history

- Method: GET
- URL: `http://localhost:5000/api/quiz/history`
- Header: `Authorization: Bearer <your token>`

---

### Step 5 — Review a specific attempt

- Method: GET
- URL: `http://localhost:5000/api/quiz/attempt/1`
- Header: `Authorization: Bearer <your token>`

---

## Adaptive Difficulty — How to See It Working

1. Start a quiz on "Algorithms"
2. Submit it with mostly correct answers (score ≥ 80%)
3. Start ANOTHER quiz on "Algorithms"
4. Look at the `difficulty` field in the response
5. It should now show `2` (Medium) instead of `1` (Easy)!

This is the adaptive engine promoting the student to harder content.

---

## Common Errors and Fixes

| Error | What it means | Fix |
|-------|---------------|-----|
| `"Topic 'X' not found"` | Topic doesn't match any in DB | Run `python seed_data.py` first |
| `404` on submit | Attempt already submitted | Start a new quiz first |
| `"answers cannot be empty"` | Forgot the answers list | Include all answers in body |
| `401 Unauthorized` | No token | Add Authorization header |
| `0 topics available` | No questions seeded | Run `python seed_data.py` |

---

## Stage 4 Checklist

- [ ] `python app.py` starts without errors
- [ ] `python test_quiz.py` shows 10/10 tests passing
- [ ] Thunder Client: GET /api/quiz/topics → see topic list
- [ ] Thunder Client: GET /api/quiz/start?topic=Algorithms → get questions (no correct_answer in response)
- [ ] Thunder Client: POST /api/quiz/submit → get score + explanations
- [ ] Thunder Client: Submit same attempt again → get 404
- [ ] Thunder Client: GET /api/quiz/history → see completed quiz
- [ ] Start a second quiz — difficulty adapts based on first score

---

## Ready for Stage 5?

Once all 8 checklist items are ticked, reply **"Start Stage 5"** and we will
build the **Analytics Dashboard** — performance charts, at-risk student
detection, and topic breakdown stats for both students and instructors! 📊
