# ⚛️ Stage 6 — React Frontend
# Setup Guide (Windows)

---

## What Was Built in Stage 6

| File | What it does |
|------|--------------|
| `frontend/package.json` | Lists all React packages to install |
| `frontend/public/index.html` | The single HTML page React renders into |
| `frontend/src/index.js` | Mounts the React app |
| `frontend/src/App.js` | All page routes and route guards |
| `frontend/src/styles/global.css` | All styling for every page |
| `frontend/src/api/api.js` | All HTTP calls to the Flask backend |
| `frontend/src/context/AuthContext.js` | Global login state |
| `frontend/src/components/Layout.js` | Sidebar + main content shell |
| `frontend/src/pages/AuthPages.js` | Login and Register pages |
| `frontend/src/pages/DashboardPage.js` | Student dashboard + Instructor dashboard |
| `frontend/src/pages/QuizPage.js` | 3-phase adaptive quiz (setup → quiz → results) |
| `frontend/src/pages/ChatbotPage.js` | Q&A chatbot with feedback |
| `frontend/src/pages/AnalyticsPage.js` | Analytics + Leaderboard pages |

---

## Step-by-Step Setup

### Step 1 — Extract the ZIP and open in VS Code

Download `ITS_Project_Stage6.zip`, extract it, and open the
`ITS_Project` folder in VS Code (File → Open Folder).

Your project now has TWO main folders:
```
ITS_Project/
├── backend/    ← Flask Python server (Stages 1–5)
└── frontend/   ← React web app      (Stage 6)
```

---

### Step 2 — Keep the Flask backend running

Open Terminal 1 (press Ctrl + backtick):

```
cd backend
venv\Scripts\activate
python app.py
```

Leave this running. You should see:
```
🤖 QA Engine ready — 10 knowledge articles loaded.
🚀 ITS Backend server starting on http://localhost:5000
```

---

### Step 3 — Install React packages

Open Terminal 2 (click `+` in the terminal panel):

```
cd frontend
npm install
```

This downloads all the packages listed in `package.json`:
- react, react-dom, react-router-dom
- axios (HTTP requests)
- recharts (charts and graphs)
- lucide-react (icons)
- react-hot-toast (notifications)

This may take 2–5 minutes the first time.
You will see a `node_modules` folder appear.

---

### Step 4 — Start the React development server

Still in Terminal 2, inside the `frontend` folder:

```
npm start
```

Expected output:
```
Compiled successfully!

You can now view its-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

Your browser should open automatically at `http://localhost:3000`.
If it doesn't, open Chrome and go to that URL manually.

---

### Step 5 — Test the full application

#### Register a student account
1. You will see the Login page
2. Click "Create one" to go to Register
3. Fill in your name, email, password
4. Leave role as "Student"
5. Click Create Account
6. You should land on the Dashboard

#### Explore the student features
- **Dashboard** — summary cards (empty until you do a quiz)
- **Take a Quiz** — select a topic, answer 5 questions with a timer, see results
- **Q&A Chatbot** — type "What is a linked list?" and get an answer
- **Analytics** — topic breakdown, difficulty distribution charts
- **Leaderboard** — top students (needs 2+ quizzes to appear)

#### Register an instructor account
1. Log out (button at the bottom of the sidebar)
2. Click "Create one" → Register
3. Set role to "Instructor"
4. Log in
5. The instructor sees a different dashboard with class-wide stats

---

## Page-by-Page Feature Summary

### Login / Register
- Form validation with clear error messages
- Role selector (Student / Instructor)
- Automatically redirects to dashboard after login
- Logged-in users are redirected away from these pages

### Student Dashboard
- Summary cards: quizzes, average score, accuracy, time studied
- Score-over-time line chart (updates after each quiz)
- Topic breakdown bar chart
- Weakest topic recommendation
- Recent quizzes table
- Chatbot usage stats

### Instructor Dashboard
- Class summary: total students, class average, at-risk count
- At-risk students highlighted in red (avg < 50%, 2+ quizzes)
- Full student table with status badges
- Class topic performance bar chart
- Weekly score trend line chart

### Quiz Page (3 phases)
**Phase 1 — Setup:**
- Topic dropdown (populated from the API)
- Explanation of adaptive difficulty

**Phase 2 — Taking the quiz:**
- Question with 4 answer options
- Timer counting up on each question
- Click question number dots to jump between questions
- Progress bar at the top
- Timer turns red after 60 seconds

**Phase 3 — Results:**
- Score circle (green ≥ 70%, amber ≥ 50%, red < 50%)
- Encouraging feedback message
- What difficulty to expect next time
- Every question reviewed with correct answer + explanation

### Q&A Chatbot
- Clickable suggestion chips for first-time users
- Sends questions to the NLP engine via the API
- Shows topic badge and article title above each answer
- Thumbs up / thumbs down feedback buttons
- Three-dot typing indicator while loading

### Analytics Page
- Student: radar chart (topic mastery), difficulty bar chart, topic table with progress bars
- Instructor: chatbot analytics, top topics, recent student questions

### Leaderboard
- Top 10 students by average score
- 🏆 🥈 🥉 badges for top 3
- Shows name, score, and quiz count
- Minimum 2 quizzes required to appear

---

## How the Two Servers Talk to Each Other

```
Browser (port 3000)          Flask API (port 5000)
       │                              │
       │  GET /api/quiz/topics        │
       │ ─────────────────────────►  │
       │                              │  Reads from PostgreSQL
       │  200 OK { topics: [...] }    │
       │ ◄─────────────────────────  │
       │                              │
```

The `"proxy": "http://localhost:5000"` line in `package.json`
means any request starting with `/api` is automatically
forwarded from port 3000 to port 5000. This lets both servers
run simultaneously without any cross-origin (CORS) issues.

---

## Common Errors and Fixes

| Error | What it means | Fix |
|-------|---------------|-----|
| `'react-scripts' is not recognized` | npm install not run yet | `cd frontend` → `npm install` |
| White screen with "Network Error" | Flask server not running | Start: `python app.py` |
| Charts are empty | No quiz data yet | Complete at least 1 quiz |
| Leaderboard is empty | No student has 2+ quizzes | Complete 2 quizzes |
| `npm start` hangs | Port 3000 already in use | Close other apps using port 3000 |
| Login says "Invalid email or password" | Account doesn't exist | Register first |

---

## Final Project Checklist

**Backend (Stages 1–5):**
- [ ] `python app.py` starts with QA engine loaded
- [ ] `python test_auth.py` → 10/10
- [ ] `python test_qa.py` → 10/10
- [ ] `python test_quiz.py` → 10/10
- [ ] `python test_analytics.py` → 10/10

**Frontend (Stage 6):**
- [ ] `npm install` completes without errors
- [ ] `npm start` opens browser at localhost:3000
- [ ] Login and Register pages work
- [ ] Student dashboard loads (cards show after 1 quiz)
- [ ] Quiz: pick topic → answer → see results + explanations
- [ ] Chatbot: ask "What is a stack?" → get a real answer
- [ ] Chatbot: click thumbs up → feedback saved
- [ ] Analytics: charts populate after completing quizzes
- [ ] Leaderboard: student appears after 2 quizzes
- [ ] Instructor dashboard: shows student table + at-risk list

---

## 🎉 Project Complete!

Your Intelligent Tutoring System is fully built:

| Component | Technology | Status |
|-----------|-----------|--------|
| Web interface | React 18, Recharts, Lucide | ✅ |
| REST API | Flask, JWT auth | ✅ |
| NLP chatbot | TF-IDF + cosine similarity | ✅ |
| Adaptive quiz | Performance-based difficulty | ✅ |
| Analytics | Student + Instructor dashboards | ✅ |
| Database | PostgreSQL + SQLAlchemy | ✅ |
