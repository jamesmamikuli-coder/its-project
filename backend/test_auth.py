# ============================================================
#  test_auth.py  — AUTOMATED AUTH TESTS
#
#  HOW TO RUN:
#  1. Terminal 1: python app.py   (keep it running)
#  2. Terminal 2: python test_auth.py
# ============================================================

import requests, json

BASE_URL = "http://localhost:5000/api"
GREEN  = "\033[92m"; RED = "\033[91m"; YELLOW = "\033[93m"; RESET = "\033[0m"
passed = 0; failed = 0
STUDENT_TOKEN = None; INSTRUCTOR_TOKEN = None


def check(name, condition, hint=""):
    global passed, failed
    if condition:
        print(f"  {GREEN}PASS{RESET}  {name}"); passed += 1
    else:
        print(f"  {RED}FAIL{RESET}  {name}")
        if hint: print(f"       {YELLOW}Hint: {hint}{RESET}")
        failed += 1

def section(title):
    print(f"\n{'='*52}\n  {title}\n{'='*52}")


# ── TEST 1: Register student ─────────────────────────────────
section("TEST 1: Register a new student")
reg_data = {"name":"Test Student","email":"teststudent_s2@example.com",
            "password":"testpass123","role":"student"}
r = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
check("Status 201 Created", r.status_code == 201, f"Got {r.status_code}: {r.text[:150]}")
if r.status_code == 201:
    b = r.json()
    check("Has 'token'",    "token" in b)
    check("Has 'user'",     "user"  in b)
    check("Role=student",   b.get("user",{}).get("role") == "student")
    check("No password in response", "password" not in json.dumps(b),
          "SECURITY: password hash must never be sent back!")
    STUDENT_TOKEN = b.get("token")


# ── TEST 2: Duplicate email rejected ─────────────────────────
section("TEST 2: Duplicate email rejected")
r2 = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
check("Status 409 Conflict", r2.status_code == 409, f"Got {r2.status_code}")
check("Error message returned", "error" in r2.json())


# ── TEST 3: Weak password rejected ───────────────────────────
section("TEST 3: Weak password rejected")
r3 = requests.post(f"{BASE_URL}/auth/register",
    json={"name":"X","email":"weak_s2@example.com","password":"abc","role":"student"})
check("Status 400 Bad Request", r3.status_code == 400, f"Got {r3.status_code}")


# ── TEST 4: Login with correct credentials ───────────────────
section("TEST 4: Login with correct credentials")
r4 = requests.post(f"{BASE_URL}/auth/login",
    json={"email":"teststudent_s2@example.com","password":"testpass123"})
check("Status 200 OK", r4.status_code == 200, f"Got {r4.status_code}: {r4.text[:150]}")
if r4.status_code == 200:
    b4 = r4.json()
    check("Has 'token'",   "token"   in b4)
    check("Has 'message'", "message" in b4)
    STUDENT_TOKEN = b4.get("token")


# ── TEST 5: Wrong password rejected ──────────────────────────
section("TEST 5: Wrong password rejected")
r5 = requests.post(f"{BASE_URL}/auth/login",
    json={"email":"teststudent_s2@example.com","password":"wrongpassword99"})
check("Status 401 Unauthorized", r5.status_code == 401, f"Got {r5.status_code}")
check("Vague error message", "Invalid email or password" in r5.json().get("error",""))


# ── TEST 6: Get profile with token ───────────────────────────
section("TEST 6: Get profile with valid token")
if STUDENT_TOKEN:
    hdrs = {"Authorization": f"Bearer {STUDENT_TOKEN}"}
    r6 = requests.get(f"{BASE_URL}/auth/me", headers=hdrs)
    check("Status 200", r6.status_code == 200, f"Got {r6.status_code}")
    if r6.status_code == 200:
        u = r6.json().get("user", {})
        check("Correct name", u.get("name") == "Test Student", f"Got: {u.get('name')}")
        check("Email returned", "email" in u)


# ── TEST 7: No token blocked ──────────────────────────────────
section("TEST 7: No token is blocked (401)")
r7 = requests.get(f"{BASE_URL}/auth/me")
check("Status 401 Unauthorized", r7.status_code == 401, f"Got {r7.status_code}")


# ── TEST 8: Register instructor ───────────────────────────────
section("TEST 8: Register an instructor")
r8 = requests.post(f"{BASE_URL}/auth/register",
    json={"name":"Prof Instructor","email":"instructor_s2@example.com",
          "password":"instructor123","role":"instructor"})
check("Status 201 Created", r8.status_code == 201, f"Got {r8.status_code}: {r8.text[:150]}")
if r8.status_code == 201:
    b8 = r8.json()
    check("Role=instructor", b8.get("user",{}).get("role") == "instructor")
    INSTRUCTOR_TOKEN = b8.get("token")


# ── TEST 9: Instructor lists users ────────────────────────────
section("TEST 9: Instructor can list all users")
if INSTRUCTOR_TOKEN:
    hdrs_i = {"Authorization": f"Bearer {INSTRUCTOR_TOKEN}"}
    r9 = requests.get(f"{BASE_URL}/auth/users", headers=hdrs_i)
    check("Status 200", r9.status_code == 200, f"Got {r9.status_code}")
    if r9.status_code == 200:
        d9 = r9.json()
        check("Has 'users' list",  isinstance(d9.get("users"), list))
        check("Has 'total' count", "total" in d9)
        check("At least 2 users",  d9.get("total", 0) >= 2, f"Got {d9.get('total')}")


# ── TEST 10: Student blocked from instructor route ────────────
section("TEST 10: Student blocked from instructor-only route")
if STUDENT_TOKEN:
    hdrs_s = {"Authorization": f"Bearer {STUDENT_TOKEN}"}
    r10 = requests.get(f"{BASE_URL}/auth/users", headers=hdrs_s)
    check("Status 403 Forbidden", r10.status_code == 403, f"Got {r10.status_code}")
    check("Access denied message", "Access denied" in r10.json().get("error",""),
          f"Error: {r10.json().get('error')}")


# ── SUMMARY ───────────────────────────────────────────────────
total = passed + failed
print(f"\n{'='*52}")
print(f"  RESULTS: {passed}/{total} tests passed")
if failed == 0:
    print(f"  {GREEN}All tests passed! Auth is working correctly.{RESET}")
else:
    print(f"  {RED}{failed} test(s) failed — read the hints above.{RESET}")
    print(f"  {YELLOW}  Make sure: python app.py is running in Terminal 1{RESET}")
print("="*52 + "\n")
