# 🤖 Stage 3 — NLP Question Answering Engine
# Setup Guide (Windows)

---

## What Was Built in Stage 3

| File | Status | What it does |
|------|--------|--------------|
| `services/qa_engine.py` | NEW | The NLP brain — TF-IDF search engine |
| `routes/qa_routes.py` | UPDATED | 4 chatbot API endpoints (was a placeholder) |
| `app.py` | UPDATED | Now trains the QA engine on startup |
| `requirements.txt` | UPDATED | Added scikit-learn, numpy, nltk |
| `test_qa.py` | NEW | 10 automated tests for the QA engine |

---

## How the NLP Engine Works (Plain English)

When a student types "What is a linked list?", here is what happens:

```
Student types:  "What is a linked list?"
                        │
                        ▼
              ┌─────────────────────┐
              │  Step 1: Clean text │
              │  "what linked list" │  (remove stopwords like "is", "a")
              └─────────────────────┘
                        │
                        ▼
              ┌──────────────────────────┐
              │  Step 2: TF-IDF          │
              │  Convert to numbers      │
              │  [0.0, 0.8, 0.0, 0.3...] │
              └──────────────────────────┘
                        │
                        ▼
              ┌──────────────────────────────────────┐
              │  Step 3: Compare to all 10 articles  │
              │  Article 1 (Linked List):  0.87 ✅   │
              │  Article 2 (Stack):        0.03      │
              │  Article 3 (Queue):        0.02      │
              │  Article 4 (BFS/DFS):      0.01      │
              └──────────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────────────┐
              │  Step 4: Return best    │
              │  if score > 0.12        │
              │  → return Article 1     │
              │  else → "I don't know"  │
              └─────────────────────────┘
```

---

## Step-by-Step: How to Add the New Files

### Step 1 — Extract the ZIP and open in VS Code

Download `ITS_Project_Stage3.zip`, extract it, and open the
`ITS_Project` folder in VS Code (File → Open Folder).

Your file tree should now look like this:

```
ITS_Project/
└── backend/
    ├── app.py                     ← UPDATED (now starts QA engine)
    ├── requirements.txt           ← UPDATED (added ML packages)
    ├── test_qa.py                 ← NEW FILE
    ├── services/
    │   ├── qa_engine.py           ← NEW FILE (the NLP brain)
    │   └── db_service.py
    └── routes/
        └── qa_routes.py           ← UPDATED (real endpoints now)
```

---

### Step 2 — Open the terminal and activate the virtual environment

Press `Ctrl + backtick` to open the terminal.

```
cd backend
venv\Scripts\activate
```

You must see `(venv)` at the start of the line.

---

### Step 3 — Install the new NLP packages

Stage 3 adds three new Python packages. Install them with:

```
pip install -r requirements.txt
```

This will install scikit-learn, numpy, and nltk.
scikit-learn is the large one — it may take 2-3 minutes.

To verify they installed correctly:
```
python -c "import sklearn; import numpy; print('NLP packages ready!')"
```

You should see: `NLP packages ready!`

---

### Step 4 — Make sure the database is seeded

The QA engine reads knowledge articles from the database.
If you haven't run seed_data.py yet (or you want to re-seed):

```
python seed_data.py
```

Expected output:
```
📝 Seeding quiz questions...
   ✅ Added 18 questions.
📚 Seeding knowledge base articles...
   ✅ Added 10 articles.
🎉 Database seeding complete!
```

---

### Step 5 — Start the Flask server

```
python app.py
```

You should now see this NEW line in the startup output:

```
✅ Database tables created / verified.
🤖 QA Engine ready — 10 knowledge articles loaded.
🚀 ITS Backend server starting on http://localhost:5000
```

The line `QA Engine ready` confirms the NLP engine trained successfully.

---

### Step 6 — Run the automated tests

Open a second terminal (click `+` in the terminal panel), then:

```
cd backend
venv\Scripts\activate
python test_qa.py
```

Expected output:

```
=====================================================
  TEST 1: Ask a question about Data Structures
=====================================================
  ✅ PASS  Status code is 200
  ✅ PASS  Response has 'found' field
  ✅ PASS  Response has 'answer' field
  ✅ PASS  Response has 'log_id'
  ✅ PASS  Answer was found
  ✅ PASS  Topic is Data Structures
...
=====================================================
  RESULTS: 10/10 tests passed
  🎉 All tests passed! Q&A engine is working correctly.
=====================================================
```

---

## All Q&A Endpoints

| Method | URL | Who | What it does |
|--------|-----|-----|--------------|
| POST | /api/qa/ask | Logged in | Submit question, get answer |
| GET | /api/qa/history | Logged in | See my past Q&A conversations |
| POST | /api/qa/feedback | Logged in | Rate an answer helpful/not |
| GET | /api/qa/suggestions | Logged in | Get sample questions to ask |

---

## Manual Testing with Thunder Client

### Test: Ask a question

- Method: POST
- URL: `http://localhost:5000/api/qa/ask`
- Header: `Authorization: Bearer <your token>`
- Body JSON:
```json
{
    "question": "What is a stack data structure?"
}
```

Expected response:
```json
{
    "found": true,
    "answer": "A stack is an abstract data type that follows the LIFO...",
    "title": "What is a Stack?",
    "topic": "Data Structures",
    "confidence": 0.7412,
    "log_id": 1
}
```

### Test: Ask something the engine doesn't know

```json
{
    "question": "What is the best football team in Nigeria?"
}
```

Expected response:
```json
{
    "found": false,
    "answer": "I couldn't find a good answer to that question...",
    "confidence": 0.0
}
```

### Test: Get history

- Method: GET
- URL: `http://localhost:5000/api/qa/history`
- Header: `Authorization: Bearer <your token>`

### Test: Rate an answer

Use the `log_id` from a previous /ask response:
- Method: POST
- URL: `http://localhost:5000/api/qa/feedback`
- Body JSON:
```json
{
    "log_id": 1,
    "was_helpful": true
}
```

### Test: Get suggestions

- Method: GET
- URL: `http://localhost:5000/api/qa/suggestions`
- Header: `Authorization: Bearer <your token>`

---

## Questions the Engine Can Answer

The engine is trained on 10 knowledge articles covering:

| Topic | Articles |
|-------|----------|
| Data Structures | Linked Lists, Stacks, Queues |
| Algorithms | Big O Notation, Binary Search, DFS vs BFS |
| Databases | SQL Commands, Normalisation |
| Programming Concepts | OOP (4 Pillars), Recursion |

Try asking in different ways — the engine handles paraphrasing:
- "What is a stack?" ✅
- "How does a stack work?" ✅
- "Explain the stack data structure" ✅
- "Tell me about LIFO" ✅

---

## Common Errors and Fixes

| Error | What it means | Fix |
|-------|---------------|-----|
| `QA engine init skipped: No module named 'sklearn'` | scikit-learn not installed | Run `pip install -r requirements.txt` |
| `No knowledge articles found` | Database not seeded | Run `python seed_data.py` |
| `found: false` for everything | Engine not fitted | Check that seed_data ran and server started correctly |
| `401 Unauthorized` | No token | Add Authorization header |

---

## Stage 3 Checklist

- [ ] `pip install -r requirements.txt` completes without errors
- [ ] `python -c "import sklearn; print('OK')"` prints OK
- [ ] `python seed_data.py` seeds 10 knowledge articles
- [ ] `python app.py` shows `QA Engine ready — 10 knowledge articles loaded`
- [ ] `python test_qa.py` shows 10/10 tests passing
- [ ] Thunder Client: ask "What is a stack?" → get a real answer
- [ ] Thunder Client: ask nonsense → get `found: false`
- [ ] Thunder Client: GET /api/qa/history → see your past questions

---

## Ready for Stage 4?

Once all 8 checklist items are ticked, reply **"Start Stage 4"** and we will
build the **Adaptive Quiz Engine** — it chooses Easy, Medium, or Hard
questions based on how each student is performing! 📝
