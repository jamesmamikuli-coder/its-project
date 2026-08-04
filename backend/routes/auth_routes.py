# ============================================================
#  routes/auth_routes.py
#  AUTHENTICATION API ENDPOINTS
#
#  A "Blueprint" is Flask's way of grouping related routes.
#  We register this blueprint in app.py with prefix /api/auth
#  so every URL in this file starts with /api/auth/...
#
#  ENDPOINTS IN THIS FILE:
#  ┌────────┬────────────────────────────┬──────────────────┐
#  │ Method │ URL                        │ Who can use it   │
#  ├────────┼────────────────────────────┼──────────────────┤
#  │ POST   │ /api/auth/register         │ Anyone           │
#  │ POST   │ /api/auth/login            │ Anyone           │
#  │ GET    │ /api/auth/me               │ Logged-in users  │
#  │ PUT    │ /api/auth/me               │ Logged-in users  │
#  │ PUT    │ /api/auth/change-password  │ Logged-in users  │
#  │ GET    │ /api/auth/users            │ Instructors only │
#  │ GET    │ /api/auth/users/<id>       │ Instructors only │
#  │ DELETE │ /api/auth/users/<id>       │ Instructors only │
#  └────────┴────────────────────────────┴──────────────────┘
#
#  HTTP STATUS CODES USED IN THIS FILE:
#  200 OK           → request succeeded, returning existing data
#  201 Created      → request succeeded, new record was created
#  400 Bad Request  → client sent invalid or missing data
#  401 Unauthorized → no valid login token provided
#  403 Forbidden    → logged in but not allowed to do this
#  404 Not Found    → the requested resource does not exist
#  409 Conflict     → request conflicts with existing data (duplicate email)
# ============================================================

import re   # Python's regular expression library — for email format checking

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models.models import User
from middleware.auth_middleware import (
    login_required,
    instructor_required,
    get_current_user
)

# ── Create the Blueprint ──────────────────────────────────────
# "auth" is just the internal name Flask uses.
# The actual URL prefix (/api/auth) is set in app.py.
auth_bp = Blueprint("auth", __name__)


# ============================================================
#  SMALL HELPER FUNCTIONS
#  These are not endpoints — they're just utilities used below.
# ============================================================

def is_valid_email(email):
    """
    Returns True if the email looks like a real email address.

    Uses a regex pattern. Don't worry about memorising regex —
    just know it checks for the format: something@something.something

    Examples:
      "amina@example.com"  → True   ✅
      "aminaexample.com"   → False  ❌  (missing @)
      "amina@"             → False  ❌  (nothing after @)
    """
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def validate_password_strength(password):
    """
    Checks if a password is strong enough.
    Returns a LIST of problems (empty list = password is acceptable).

    We return a list so we can tell the user EVERY problem at once
    instead of showing one error, they fix it, then another pops up.

    Rules enforced:
      - At least 8 characters long
      - Must contain at least one digit (0-9)

    Examples:
      "pass"       → ["must be 8+ chars", "must have a number"]
      "password"   → ["must have a number"]
      "password1"  → []   ✅
    """
    problems = []

    if len(password) < 8:
        problems.append("Password must be at least 8 characters long.")

    # any(condition for char in string) = True if ANY char meets condition
    if not any(char.isdigit() for char in password):
        problems.append("Password must contain at least one number.")

    return problems


# ============================================================
#  ENDPOINT 1 — REGISTER
#  POST /api/auth/register
# ============================================================
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Create a brand new user account.

    ── WHAT THE FRONTEND SENDS (JSON body) ──
    {
        "name":     "Amina Bello",
        "email":    "amina@university.com",
        "password": "securepass123",
        "role":     "student"
    }
    NOTE: "role" is optional. If you leave it out, it defaults to "student".

    ── WHAT THIS FUNCTION DOES, STEP BY STEP ──
    1.  Read the JSON data from the request body
    2.  Validate all fields (not empty, correct format, strong password)
    3.  Check the email isn't already taken by another account
    4.  Hash the password (never store plain text passwords!)
    5.  Save the new User to the database
    6.  Create a JWT token so they're immediately logged in
    7.  Return the token + user profile

    ── WHAT THE FRONTEND RECEIVES BACK ──
    {
        "message": "Welcome, Amina Bello! Your account has been created.",
        "token":   "eyJhbGci...",
        "user": {
            "id":    1,
            "name":  "Amina Bello",
            "email": "amina@university.com",
            "role":  "student"
        }
    }
    """

    # ── Step 1: Read JSON from request ───────────────────────
    # request.get_json() reads the HTTP request body and
    # parses it from a JSON string into a Python dictionary.
    # If the body is empty or not valid JSON, it returns None.
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    # ── Step 2: Check all required fields are present ────────
    # data.get("name", "") means: get "name", return "" if missing
    # .strip() removes whitespace from both ends of the string
    # So "   " (just spaces) becomes "" after strip(), which is falsy
    required_fields = ["name", "email", "password"]
    missing_fields  = [f for f in required_fields
                       if not data.get(f, "").strip()]

    if missing_fields:
        return jsonify({
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400

    # ── Step 3: Clean up and extract the values ───────────────
    name     = data["name"].strip()
    email    = data["email"].strip().lower()  # Always lowercase emails
    password = data["password"]               # Don't strip — spaces in passwords are valid
    role     = data.get("role", "student").strip().lower()

    # ── Step 4: Validate each field ──────────────────────────
    if len(name) < 2:
        return jsonify({"error": "Name must be at least 2 characters."}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Please enter a valid email address."}), 400

    pw_problems = validate_password_strength(password)
    if pw_problems:
        return jsonify({"error": " ".join(pw_problems)}), 400

    if role not in ["student", "instructor"]:
        return jsonify({"error": "Role must be either 'student' or 'instructor'."}), 400

    # ── Step 5: Check email not already registered ────────────
    # This runs SQL: SELECT * FROM users WHERE email = '...' LIMIT 1
    if User.query.filter_by(email=email).first():
        return jsonify({
            "error": "An account with this email address already exists."
        }), 409  # 409 Conflict

    # ── Step 6: Hash the password ─────────────────────────────
    # NEVER store plain text passwords in a database!
    # If the database is ever leaked, hashed passwords are useless to attackers.
    # generate_password_hash("mypass1") might produce:
    # "pbkdf2:sha256:260000$xK2abc$3f8e7d..."  (a safe one-way hash)
    hashed_pw = generate_password_hash(password)

    # ── Step 7: Create and save the new User ─────────────────
    new_user = User(
        name     = name,
        email    = email,
        password = hashed_pw,
        role     = role
    )
    db.session.add(new_user)    # Stage the INSERT
    db.session.commit()          # Execute it on the database

    # ── Step 8: Create JWT token ──────────────────────────────
    # identity = what we use to identify this user on future requests
    # We store their ID as a string (JWT requires string identity)
    # additional_claims = extra data baked into the token (we store role)
    token = create_access_token(
        identity          = str(new_user.id),
        additional_claims = {"role": new_user.role}
    )

    # ── Step 9: Return success response ──────────────────────
    return jsonify({
        "message": f"Welcome, {new_user.name}! Your account has been created.",
        "token":   token,
        "user":    new_user.to_dict()
    }), 201  # 201 Created


# ============================================================
#  ENDPOINT 2 — LOGIN
#  POST /api/auth/login
# ============================================================
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Log in with an existing account and receive a JWT token.

    ── WHAT THE FRONTEND SENDS ──
    {
        "email":    "amina@university.com",
        "password": "securepass123"
    }

    ── SECURITY NOTE ──
    We return the same error message whether:
    (a) The email doesn't exist in our database, OR
    (b) The password is wrong
    This is intentional — we don't want to leak information
    about which emails are registered in our system.
    """

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are both required."}), 400

    email    = data["email"].strip().lower()
    password = data["password"]

    # Find the user by email in the database
    user = User.query.filter_by(email=email).first()

    # check_password_hash(stored_hash, plain_password):
    # It hashes the plain_password the same way and compares.
    # Returns True if they match, False if not.
    # We check BOTH at once with 'or' — same error either way.
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password."}), 401

    # Create a fresh JWT token for this login session
    token = create_access_token(
        identity          = str(user.id),
        additional_claims = {"role": user.role}
    )

    return jsonify({
        "message": f"Welcome back, {user.name}!",
        "token":   token,
        "user":    user.to_dict()
    }), 200


# ============================================================
#  ENDPOINT 3 — GET MY PROFILE
#  GET /api/auth/me
# ============================================================
@auth_bp.route("/me", methods=["GET"])
@login_required
def get_me():
    """
    Returns the profile of whoever is currently logged in.

    The frontend sends the JWT token in the HTTP header:
        Authorization: Bearer eyJhbGci...

    The @login_required decorator (from middleware/auth_middleware.py):
      1. Reads that Authorization header
      2. Verifies the token is valid and not expired
      3. Loads the User from the database using the ID in the token
      4. Stores the User on g.current_user for us to use

    Then get_current_user() retrieves it — no extra DB query needed.
    """
    user = get_current_user()
    return jsonify({"user": user.to_dict()}), 200


# ============================================================
#  ENDPOINT 4 — UPDATE MY PROFILE
#  PUT /api/auth/me
# ============================================================
@auth_bp.route("/me", methods=["PUT"])
@login_required
def update_me():
    """
    Update the current user's name and/or email.

    ── WHAT THE FRONTEND SENDS (all fields are optional) ──
    {
        "name":  "New Name",
        "email": "newemail@example.com"
    }

    Only fields you include get updated.
    Fields you leave out stay the same.
    """
    user = get_current_user()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    # ── Update name (if it was sent) ──────────────────────────
    # "if 'name' in data" checks if the key exists in the dictionary
    # This is different from "if data.get('name')" which would be
    # False for empty strings — we want to catch those too and error
    if "name" in data:
        new_name = data["name"].strip()
        if len(new_name) < 2:
            return jsonify({"error": "Name must be at least 2 characters."}), 400
        user.name = new_name

    # ── Update email (if it was sent) ─────────────────────────
    if "email" in data:
        new_email = data["email"].strip().lower()

        if not is_valid_email(new_email):
            return jsonify({"error": "Please enter a valid email address."}), 400

        # Check if another user already has this email
        # We allow keeping the same email (existing.id == user.id)
        existing = User.query.filter_by(email=new_email).first()
        if existing and existing.id != user.id:
            return jsonify({
                "error": "That email address is already in use by another account."
            }), 409

        user.email = new_email

    # SQLAlchemy tracks changes automatically — just commit
    db.session.commit()

    return jsonify({
        "message": "Profile updated successfully.",
        "user":    user.to_dict()
    }), 200


# ============================================================
#  ENDPOINT 5 — CHANGE PASSWORD
#  PUT /api/auth/change-password
# ============================================================
@auth_bp.route("/change-password", methods=["PUT"])
@login_required
def change_password():
    """
    Change the logged-in user's password.

    Requires the CURRENT password first — this is a security
    measure so someone who briefly has access to your open browser
    can't change your password without knowing the old one.

    ── WHAT THE FRONTEND SENDS ──
    {
        "current_password": "oldpassword1",
        "new_password":     "newpassword2"
    }
    """
    user = get_current_user()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    current_pw = data.get("current_password", "")
    new_pw     = data.get("new_password", "")

    if not current_pw or not new_pw:
        return jsonify({
            "error": "Both current_password and new_password are required."
        }), 400

    # Verify they actually know the current password
    if not check_password_hash(user.password, current_pw):
        return jsonify({"error": "Current password is incorrect."}), 401

    # Validate the new password meets our rules
    problems = validate_password_strength(new_pw)
    if problems:
        return jsonify({"error": " ".join(problems)}), 400

    # Hash and save the new password
    user.password = generate_password_hash(new_pw)
    db.session.commit()

    return jsonify({"message": "Password changed successfully."}), 200


# ============================================================
#  ENDPOINT 6 — LIST ALL USERS (INSTRUCTOR ONLY)
#  GET /api/auth/users
#  GET /api/auth/users?role=student
#  GET /api/auth/users?search=amina
# ============================================================
@auth_bp.route("/users", methods=["GET"])
@instructor_required
def list_users():
    """
    Returns a list of all registered users.
    Only instructors can call this.

    ── OPTIONAL FILTERS IN THE URL ──
    ?role=student        → only students
    ?role=instructor     → only instructors
    ?search=amina        → name or email contains "amina"

    ── EXAMPLE URLS ──
    GET /api/auth/users
    GET /api/auth/users?role=student
    GET /api/auth/users?search=bello
    GET /api/auth/users?role=student&search=amina
    """
    query = User.query

    # request.args.get() reads URL query parameters
    # For /users?role=student it returns "student"
    # For /users (no ?role) it returns None
    role_filter = request.args.get("role")
    if role_filter:
        query = query.filter_by(role=role_filter)

    search_term = request.args.get("search")
    if search_term:
        # ilike = case-insensitive LIKE
        # "%amina%" matches any string containing "amina" anywhere
        wildcard = f"%{search_term}%"
        query = query.filter(
            User.name.ilike(wildcard) | User.email.ilike(wildcard)
        )

    # Order newest accounts first
    users = query.order_by(User.created_at.desc()).all()

    return jsonify({
        "users": [u.to_dict() for u in users],
        "total": len(users)
    }), 200


# ============================================================
#  ENDPOINT 7 — GET ONE USER (INSTRUCTOR ONLY)
#  GET /api/auth/users/<id>
# ============================================================
@auth_bp.route("/users/<int:user_id>", methods=["GET"])
@instructor_required
def get_user(user_id):
    """
    Returns one specific user's profile.

    <int:user_id> tells Flask to:
    1. Extract the number from the URL (e.g. /users/5 gives 5)
    2. Convert it to a Python integer
    3. Pass it to this function as the user_id parameter

    Example: GET /api/auth/users/5
    """
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": f"No user found with ID {user_id}."}), 404

    return jsonify({"user": user.to_dict()}), 200


# ============================================================
#  ENDPOINT 8 — DELETE A USER (INSTRUCTOR ONLY)
#  DELETE /api/auth/users/<id>
# ============================================================
@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@instructor_required
def delete_user(user_id):
    """
    Permanently deletes a user account.

    Because we set cascade="all, delete-orphan" in models.py,
    deleting a user ALSO automatically deletes all their:
    - Quiz attempts and answers
    - Q&A chatbot log entries

    This keeps the database clean with no orphaned records.
    """
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": f"No user found with ID {user_id}."}), 404

    name = user.name  # Save before deleting so we can use it in the message

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": f"User '{name}' has been deleted successfully."
    }), 200
