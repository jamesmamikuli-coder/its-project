# 🚀 Stage 1 Setup Guide — Windows

Follow every step in order. Don't skip any step!

---

## STEP 1 — Install Required Software

Install these **4 tools** before anything else:

| Tool | Download | Notes |
|------|----------|-------|
| Python 3.11 | https://python.org/downloads | ✅ Tick "Add Python to PATH" during install |
| Node.js LTS | https://nodejs.org | Choose the LTS (Long Term Support) version |
| PostgreSQL 16 | https://postgresql.org/download/windows | Remember the password you set for user 'postgres' |
| VS Code | https://code.visualstudio.com | Recommended editor |

### Verify installations
Open **Command Prompt** (press `Win + R`, type `cmd`, press Enter) and run:
```
python --version
node --version
npm --version
psql --version
```
All four should print a version number. If any say "not recognized", restart your computer and try again.

---

## STEP 2 — Create the PostgreSQL Database

1. Open **pgAdmin 4** (installed with PostgreSQL — find it in Start Menu)
2. Log in with the password you set during PostgreSQL installation
3. In the left panel, right-click **Databases** → **Create** → **Database**
4. Name it: `its_db`
5. Click **Save**

✅ You should now see `its_db` in the Databases list.

**Alternative (Command Line):**
```
psql -U postgres
CREATE DATABASE its_db;
\q
```

---

## STEP 3 — Set Up the Project Folder

1. Open **VS Code**
2. Open the `ITS_Project` folder: File → Open Folder → select `ITS_Project`
3. Open the **Terminal** inside VS Code: Terminal → New Terminal

---

## STEP 4 — Create Python Virtual Environment

In the VS Code terminal, navigate to the backend folder:
```
cd backend
```

Create a virtual environment (an isolated Python environment for this project):
```
python -m venv venv
```

Activate it:
```
venv\Scripts\activate
```

You should see `(venv)` appear at the start of your terminal line.
**Always activate the venv before running backend code!**

---

## STEP 5 — Install Python Packages

With the venv activated, install all packages:
```
pip install -r requirements.txt
```

This will take 2–5 minutes. You'll see lots of text — that's normal.

---

## STEP 6 — Configure Your Database Password

1. In the `backend` folder, find the file called `.env.example`
2. Make a copy of it and rename the copy to `.env`
3. Open `.env` and change `postgres:postgres` to `postgres:YOUR_PASSWORD`
   - Replace `YOUR_PASSWORD` with the password you set when installing PostgreSQL

Example — if your PostgreSQL password is `mypassword123`:
```
DATABASE_URL=postgresql://postgres:mypassword123@localhost:5432/its_db
```

---

## STEP 7 — Start the Flask Backend Server

In the VS Code terminal (with venv activated, inside the `backend` folder):
```
python app.py
```

You should see:
```
✅ Database tables created / verified.
🚀 ITS Backend server starting on http://localhost:5000
 * Running on http://127.0.0.1:5000
```

---

## STEP 8 — Seed the Database with Sample Data

Open a **second terminal** in VS Code (click the `+` icon in the terminal panel).
Navigate to backend and activate venv:
```
cd backend
venv\Scripts\activate
python seed_data.py
```

You should see:
```
📝 Seeding quiz questions...
   ✅ Added 18 questions.
📚 Seeding knowledge base articles...
   ✅ Added 10 articles.
🎉 Database seeding complete!
```

---

## STEP 9 — Test the API

Open your web browser and go to:
```
http://localhost:5000/api/auth/me
```

You should see a JSON response (even if it's an error about missing token — that means the server is working!).

**Better test using a tool like:**
- **Thunder Client** (VS Code extension — search for it in the Extensions panel)
- Or **Postman** (free download at postman.com)

**Test registration:**
- Method: POST
- URL: `http://localhost:5000/api/auth/register`
- Body (JSON):
```json
{
    "name": "Test Student",
    "email": "test@example.com",
    "password": "password123",
    "role": "student"
}
```

**Expected response:**
```json
{
    "message": "Account created successfully!",
    "token": "eyJ...",
    "user": { "id": 1, "name": "Test Student", ... }
}
```

---

## ✅ Stage 1 Complete Checklist

- [ ] Python, Node.js, PostgreSQL, VS Code installed
- [ ] `its_db` database created in pgAdmin
- [ ] Virtual environment created and activated
- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with your PostgreSQL password
- [ ] `python app.py` runs without errors
- [ ] `python seed_data.py` runs and seeds the database
- [ ] Registration API returns a token

---

## ❌ Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `python not recognized` | Reinstall Python, tick "Add to PATH". Restart PC. |
| `venv\Scripts\activate` fails | Run: `Set-ExecutionPolicy RemoteSigned` in PowerShell as Admin |
| `could not connect to server` | Make sure PostgreSQL service is running. Open Services app, find PostgreSQL, click Start. |
| `FATAL: password authentication failed` | Check your `.env` file — the password must match what you set in PostgreSQL |
| `ModuleNotFoundError` | Make sure venv is activated (you see `(venv)`) before running `pip install` |

---

## 📁 Your Current Project Structure

```
ITS_Project/
├── .gitignore
├── backend/
│   ├── app.py                  ← Main Flask entry point
│   ├── requirements.txt        ← Python package list
│   ├── seed_data.py            ← Sample data loader
│   ├── .env.example            ← Template for your .env file
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         ← All configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py           ← Database table definitions
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py      ← Login & registration (DONE ✅)
│   │   ├── qa_routes.py        ← Q&A chatbot (Stage 3)
│   │   ├── quiz_routes.py      ← Quiz engine (Stage 4)
│   │   └── analytics_routes.py ← Analytics (Stage 5)
│   └── services/
│       └── __init__.py         ← NLP services go here (Stage 3)
└── frontend/                   ← React app (Stage 6)
```

---

## ▶️ Ready for Stage 2?

Once your checklist above is all ticked, reply **"Start Stage 2"** and we'll build the full authentication system and database relationships!
