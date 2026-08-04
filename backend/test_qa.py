# ============================================================
#  test_qa.py
#  AUTOMATED TESTS FOR THE Q&A CHATBOT ENGINE
#
#  Tests both the NLP engine directly (unit tests) and the
#  API endpoints (integration tests).
#
#  HOW TO RUN:
#    1. Start your Flask server:  python app.py
#    2. Open a second terminal
#    3. Activate venv:            venv\Scripts\activate
#    4. Run:                      python test_qa.py
#
#  EXPECTED RESULT: All tests pass
# ============================================================

import requests
import sys

BASE_URL = "http://localhost:5000/api"

# Terminal colour codes
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


# ── Get a token to use in all tests ──────────────────────────
# First register (or login if already registered)
section("SETUP: Get a student token")

reg_resp = requests.post(f"{BASE_URL}/auth/register", json={
    "name":     "QA Test Student",
    "email":    "qatestuser@example.com",
    "password": "password123",
    "role":     "student"
})

if reg_resp.status_code == 201:
    TOKEN = reg_resp.json()["token"]
    print(f"  {GREEN}Registered new test user{RESET}")
elif reg_resp.status_code == 409:
    # Already registered — just login
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email":    "qatestuser@example.com",
        "password": "password123"
    })
    TOKEN = login_resp.json().get("token")
    print(f"  {GREEN}Logged in existing test user{RESET}")
else:
    print(f"  {RED}Could not get token — is the server running?{RESET}")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {TOKEN}"}


# ============================================================
#  TEST 1 — Ask a question about a known topic
# ============================================================
section("TEST 1: Ask a question about Data Structures")

r1 = requests.post(
    f"{BASE_URL}/qa/ask",
    json={"question": "What is a linked list?"},
    headers=HEADERS
)

test("Status code is 200", r1.status_code == 200,
     f"Got {r1.status_code}: {r1.text[:200]}")

if r1.status_code == 200:
    body1 = r1.json()
    test("Response has 'found' field",  "found"  in body1)
    test("Response has 'answer' field", "answer" in body1)
    test("Response has 'log_id'",       "log_id" in body1)
    test("Answer was found",            body1.get("found") == True,
         f"found={body1.get('found')}, answer={body1.get('answer')[:100]}")
    test("Topic is Data Structures",
         "data structure" in body1.get("topic", "").lower() or
         "data structures" in body1.get("topic", "").lower(),
         f"Got topic: {body1.get('topic')}")
    LOG_ID = body1.get("log_id")
else:
    LOG_ID = None


# ============================================================
#  TEST 2 — Ask about Algorithms
# ============================================================
section("TEST 2: Ask about Big O notation")

r2 = requests.post(
    f"{BASE_URL}/qa/ask",
    json={"question": "What is Big O notation and why does it matter?"},
    headers=HEADERS
)

test("Status code is 200", r2.status_code == 200)
if r2.status_code == 200:
    body2 = r2.json()
    test("Answer was found", body2.get("found") == True,
         f"answer={body2.get('answer')[:100]}")
    test("Confidence score is present",
         isinstance(body2.get("confidence"), (int, float)))


# ============================================================
#  TEST 3 — Ask about Databases
# ============================================================
section("TEST 3: Ask about SQL")

r3 = requests.post(
    f"{BASE_URL}/qa/ask",
    json={"question": "how does SQL work and what are the main commands?"},
    headers=HEADERS
)

test("Status code is 200", r3.status_code == 200)
if r3.status_code == 200:
    test("Answer was found", r3.json().get("found") == True,
         f"Got: {r3.json().get('answer')[:100]}")


# ============================================================
#  TEST 4 — Ask about OOP
# ============================================================
section("TEST 4: Ask about Object Oriented Programming")

r4 = requests.post(
    f"{BASE_URL}/qa/ask",
    json={"question": "explain the four pillars of OOP"},
    headers=HEADERS
)

test("Status code is 200", r4.status_code == 200)
if r4.status_code == 200:
    test("Answer was found", r4.json().get("found") == True,
         f"Got: {r4.json().get('answer')[:100]}")


# ============================================================
#  TEST 5 — Ask a completely unrelated question
# ============================================================
section("TEST 5: Nonsense question should return 'not found'")

r5 = requests.post(
    f"{BASE_URL}/qa/ask",
    json={"question": "xyzzy qwerty blibble florp nonsense words"},
    headers=HEADERS
)

test("Status code is 200", r5.status_code == 200)
if r5.status_code == 200:
    # The engine should NOT pretend to know the answer
    test("found=false for nonsense question",
         r5.json().get("found") == False,
         f"found={r5.json().get('found')}")


# ============================================================
#  TEST 6 — Empty question is rejected
# ============================================================
section("TEST 6: Empty question is rejected")

r6 = requests.post(
    f"{BASE_URL}/qa/ask",
    json={"question": "   "},
    headers=HEADERS
)

test("Status code is 400 (Bad Request)", r6.status_code == 400,
     f"Got {r6.status_code}")


# ============================================================
#  TEST 7 — No token is rejected
# ============================================================
section("TEST 7: No token is rejected")

r7 = requests.post(
    f"{BASE_URL}/qa/ask",
    json={"question": "What is a stack?"}
    # No headers — no token
)

test("Status code is 401 (Unauthorized)", r7.status_code == 401,
     f"Got {r7.status_code}")


# ============================================================
#  TEST 8 — Get conversation history
# ============================================================
section("TEST 8: Get Q&A conversation history")

r8 = requests.get(f"{BASE_URL}/qa/history", headers=HEADERS)

test("Status code is 200", r8.status_code == 200,
     f"Got {r8.status_code}")
if r8.status_code == 200:
    body8 = r8.json()
    test("Response has 'history' list", isinstance(body8.get("history"), list))
    test("Response has 'total' count",  "total" in body8)
    test("History has at least 1 entry", body8.get("total", 0) >= 1,
         f"Total: {body8.get('total')}")


# ============================================================
#  TEST 9 — Submit helpful feedback
# ============================================================
section("TEST 9: Submit 'helpful' feedback on an answer")

if LOG_ID:
    r9 = requests.post(
        f"{BASE_URL}/qa/feedback",
        json={"log_id": LOG_ID, "was_helpful": True},
        headers=HEADERS
    )
    test("Status code is 200", r9.status_code == 200,
         f"Got {r9.status_code}: {r9.text}")
    test("Success message returned", "message" in r9.json())
else:
    print(f"  {YELLOW}⚠ Skipping — no log_id from Test 1{RESET}")


# ============================================================
#  TEST 10 — Get suggestions
# ============================================================
section("TEST 10: Get chatbot question suggestions")

r10 = requests.get(f"{BASE_URL}/qa/suggestions", headers=HEADERS)

test("Status code is 200", r10.status_code == 200)
if r10.status_code == 200:
    body10 = r10.json()
    test("Response has 'suggestions' list",
         isinstance(body10.get("suggestions"), list))
    test("At least 4 suggestions returned",
         len(body10.get("suggestions", [])) >= 4,
         f"Got {len(body10.get('suggestions', []))} suggestions")


# ============================================================
#  SUMMARY
# ============================================================
total = passed + failed
print(f"\n{BLUE}{'='*55}{RESET}")
print(f"  RESULTS: {passed}/{total} tests passed")
if failed == 0:
    print(f"  {GREEN}🎉 All tests passed! Q&A engine is working correctly.{RESET}")
else:
    print(f"  {RED}⚠  {failed} test(s) failed. See details above.{RESET}")
    print(f"  {YELLOW}Tip: Make sure python seed_data.py has been run{RESET}")
print(f"{BLUE}{'='*55}{RESET}\n")

sys.exit(0 if failed == 0 else 1)
