# ============================================================
#  test_quiz.py
#  AUTOMATED TESTS FOR THE ADAPTIVE QUIZ ENGINE
#
#  Tests the full quiz flow from start to submission,
#  plus the adaptive difficulty logic.
#
#  HOW TO RUN:
#    1. Start Flask server:    python app.py
#    2. Open second terminal
#    3. Activate venv:         venv\Scripts\activate
#    4. Run:                   python test_quiz.py
#
#  EXPECTED RESULT: All tests pass
# ============================================================

import requests
import sys

BASE_URL = "http://localhost:5000/api"

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"

passed = 0
failed = 0


def test(description, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  {GREEN}✅ PASS{RESET}  {description}")
        passed += 1
    else:
        print(f"  {RED}❌ FAIL{RESET}  {description}")
        if detail:
            print(f"         {YELLOW}→ {detail}{RESET}")
        failed += 1


def section(title):
    print(f"\n{BLUE}{'='*55}{RESET}")
    print(f"{BLUE}  {title}{RESET}")
    print(f"{BLUE}{'='*55}{RESET}")


# ── Get a student token ───────────────────────────────────────
section("SETUP: Get a student token")

reg = requests.post(f"{BASE_URL}/auth/register", json={
    "name": "Quiz Test Student", "email": "quiztest@example.com",
    "password": "password123", "role": "student"
})
if reg.status_code == 201:
    TOKEN = reg.json()["token"]
    print(f"  {GREEN}Registered new student{RESET}")
elif reg.status_code == 409:
    login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "quiztest@example.com", "password": "password123"
    })
    TOKEN = login.json().get("token")
    print(f"  {GREEN}Logged in existing student{RESET}")
else:
    print(f"  {RED}Could not get token — is the server running?{RESET}")
    sys.exit(1)

H = {"Authorization": f"Bearer {TOKEN}"}


# ============================================================
#  TEST 1 — Get available topics
# ============================================================
section("TEST 1: Get available quiz topics")

r1 = requests.get(f"{BASE_URL}/quiz/topics", headers=H)
test("Status code is 200", r1.status_code == 200,
     f"Got {r1.status_code}: {r1.text[:200]}")

if r1.status_code == 200:
    topics = r1.json().get("topics", [])
    test("Topics list is returned",      isinstance(topics, list))
    test("At least one topic exists",    len(topics) >= 1,
         f"Got {len(topics)} topics. Run seed_data.py first.")
    print(f"         {YELLOW}Topics found: {topics}{RESET}")
    FIRST_TOPIC = topics[0] if topics else None
else:
    FIRST_TOPIC = None


# ============================================================
#  TEST 2 — Start a quiz with a valid topic
# ============================================================
section("TEST 2: Start a quiz on a valid topic")

ATTEMPT_ID = None
QUESTIONS   = []

if FIRST_TOPIC:
    r2 = requests.get(
        f"{BASE_URL}/quiz/start",
        params={"topic": FIRST_TOPIC},
        headers=H
    )
    test("Status code is 200", r2.status_code == 200,
         f"Got {r2.status_code}: {r2.text[:200]}")

    if r2.status_code == 200:
        body2 = r2.json()
        test("Response has 'attempt_id'",       "attempt_id"      in body2)
        test("Response has 'questions'",         "questions"       in body2)
        test("Response has 'difficulty'",        "difficulty"      in body2)
        test("Response has 'difficulty_label'",  "difficulty_label" in body2)
        test("At least 1 question returned",
             len(body2.get("questions", [])) >= 1,
             f"Got {len(body2.get('questions', []))} questions")
        test("Correct answer NOT in questions",
             all("correct_answer" not in q for q in body2.get("questions", [])),
             "Security issue: correct_answer should not be sent during quiz!")
        test("Difficulty is 1 (Easy) for first attempt",
             body2.get("difficulty") == 1,
             f"Got difficulty={body2.get('difficulty')} — should be 1 for new student")

        ATTEMPT_ID = body2.get("attempt_id")
        QUESTIONS  = body2.get("questions", [])
else:
    print(f"  {YELLOW}⚠ Skipping — no topics available (run seed_data.py){RESET}")


# ============================================================
#  TEST 3 — Start quiz with invalid topic
# ============================================================
section("TEST 3: Invalid topic is rejected")

r3 = requests.get(
    f"{BASE_URL}/quiz/start",
    params={"topic": "FakeTopic99999"},
    headers=H
)
test("Status code is 404 (Not Found)", r3.status_code == 404,
     f"Got {r3.status_code}")
test("Error message returned", "error" in r3.json())


# ============================================================
#  TEST 4 — Start quiz with no topic
# ============================================================
section("TEST 4: Missing topic parameter is rejected")

r4 = requests.get(f"{BASE_URL}/quiz/start", headers=H)
test("Status code is 400 (Bad Request)", r4.status_code == 400,
     f"Got {r4.status_code}")
test("Available topics listed in error", "available_topics" in r4.json())


# ============================================================
#  TEST 5 — No token is rejected
# ============================================================
section("TEST 5: No token is rejected")

r5 = requests.get(f"{BASE_URL}/quiz/start", params={"topic": "Algorithms"})
test("Status code is 401 (Unauthorized)", r5.status_code == 401,
     f"Got {r5.status_code}")


# ============================================================
#  TEST 6 — Submit a quiz with all correct answers
# ============================================================
section("TEST 6: Submit a quiz (all answers selected)")

if ATTEMPT_ID and QUESTIONS:
    # Build answers — we pick 'A' for every question
    # (some will be correct, some won't — that's fine for testing the flow)
    fake_answers = [
        {
            "question_id":     q["id"],
            "selected_answer": "A",
            "time_taken_secs": 10
        }
        for q in QUESTIONS
    ]

    r6 = requests.post(
        f"{BASE_URL}/quiz/submit",
        json={"attempt_id": ATTEMPT_ID, "answers": fake_answers},
        headers=H
    )
    test("Status code is 200", r6.status_code == 200,
         f"Got {r6.status_code}: {r6.text[:200]}")

    if r6.status_code == 200:
        body6 = r6.json()
        test("Response has 'score'",           "score"           in body6)
        test("Response has 'correct_q'",       "correct_q"       in body6)
        test("Response has 'total_q'",         "total_q"         in body6)
        test("Response has 'feedback_message'","feedback_message" in body6)
        test("Response has 'answers' list",    isinstance(body6.get("answers"), list))
        test("Score is between 0 and 100",
             0 <= body6.get("score", -1) <= 100,
             f"Got score={body6.get('score')}")
        test("Each answer shows correct_answer",
             all("correct_answer" in a for a in body6.get("answers", [])),
             "correct_answer should appear on results page")
        test("Each answer shows explanation",
             all("explanation" in a for a in body6.get("answers", [])))
        test("next_difficulty is present",
             "next_difficulty" in body6,
             "Adaptive engine should tell student what's next")
        print(f"         {YELLOW}Score: {body6.get('score')}% | "
              f"Feedback: {body6.get('feedback_message')}{RESET}")
else:
    print(f"  {YELLOW}⚠ Skipping — no attempt from Test 2{RESET}")


# ============================================================
#  TEST 7 — Cannot submit same attempt twice
# ============================================================
section("TEST 7: Cannot submit same attempt twice")

if ATTEMPT_ID and QUESTIONS:
    fake_answers = [
        {"question_id": q["id"], "selected_answer": "B", "time_taken_secs": 5}
        for q in QUESTIONS
    ]
    r7 = requests.post(
        f"{BASE_URL}/quiz/submit",
        json={"attempt_id": ATTEMPT_ID, "answers": fake_answers},
        headers=H
    )
    test("Status code is 404 (already submitted)", r7.status_code == 404,
         f"Got {r7.status_code}")
else:
    print(f"  {YELLOW}⚠ Skipping — no attempt from Test 2{RESET}")


# ============================================================
#  TEST 8 — Get quiz history
# ============================================================
section("TEST 8: Get quiz history")

r8 = requests.get(f"{BASE_URL}/quiz/history", headers=H)
test("Status code is 200", r8.status_code == 200,
     f"Got {r8.status_code}")

if r8.status_code == 200:
    body8 = r8.json()
    test("Response has 'history' list",  isinstance(body8.get("history"), list))
    test("Response has 'total' count",   "total" in body8)
    test("At least 1 quiz in history",   body8.get("total", 0) >= 1,
         f"Total: {body8.get('total')}")


# ============================================================
#  TEST 9 — Get attempt detail
# ============================================================
section("TEST 9: Get full detail of one quiz attempt")

if ATTEMPT_ID:
    r9 = requests.get(f"{BASE_URL}/quiz/attempt/{ATTEMPT_ID}", headers=H)
    test("Status code is 200", r9.status_code == 200,
         f"Got {r9.status_code}: {r9.text[:200]}")

    if r9.status_code == 200:
        body9 = r9.json()
        test("Has 'answers' list",         isinstance(body9.get("answers"), list))
        test("Has 'difficulty_label'",     "difficulty_label" in body9)
        test("Has at least 1 answer",      len(body9.get("answers", [])) >= 1)
else:
    print(f"  {YELLOW}⚠ Skipping — no attempt ID{RESET}")


# ============================================================
#  TEST 10 — Adaptive difficulty check
# ============================================================
section("TEST 10: Adaptive difficulty check after scoring high")

# Start a second quiz on the same topic
# Since we scored in test 6 (answers all 'A'), difficulty may change
if FIRST_TOPIC:
    r10 = requests.get(
        f"{BASE_URL}/quiz/start",
        params={"topic": FIRST_TOPIC},
        headers=H
    )
    test("Second quiz starts successfully", r10.status_code == 200,
         f"Got {r10.status_code}")

    if r10.status_code == 200:
        body10 = r10.json()
        diff = body10.get("difficulty")
        label = body10.get("difficulty_label")
        test("Difficulty level is valid (1, 2, or 3)", diff in [1, 2, 3],
             f"Got difficulty={diff}")
        print(f"         {YELLOW}Adaptive difficulty for 2nd quiz: "
              f"{diff} ({label}){RESET}")

        # Clean up — cancel this second attempt by not submitting
else:
    print(f"  {YELLOW}⚠ Skipping — no first topic available{RESET}")


# ============================================================
#  SUMMARY
# ============================================================
total = passed + failed
print(f"\n{BLUE}{'='*55}{RESET}")
print(f"  RESULTS: {passed}/{total} tests passed")
if failed == 0:
    print(f"  {GREEN}🎉 All tests passed! Quiz engine is working correctly.{RESET}")
else:
    print(f"  {RED}⚠  {failed} test(s) failed. See details above.{RESET}")
    print(f"  {YELLOW}Tip: Make sure seed_data.py has been run{RESET}")
print(f"{BLUE}{'='*55}{RESET}\n")

sys.exit(0 if failed == 0 else 1)
