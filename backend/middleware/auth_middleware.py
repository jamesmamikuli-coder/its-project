# ============================================================
#  middleware/auth_middleware.py
#  ROUTE PROTECTION — WHO IS ALLOWED IN?
#
#  This file contains "decorators" — special functions that
#  act like security guards in front of our API routes.
#
#  WHAT IS A DECORATOR?
#  --------------------
#  A decorator sits in front of a route function and runs
#  BEFORE the route's own code executes. If the check fails,
#  the decorator sends back an error and the route never runs.
#
#  HOW TO USE THEM:
#  ----------------
#  @login_required       → any logged-in user (student or instructor)
#  @student_required     → students only
#  @instructor_required  → instructors only
#
#  EXAMPLE:
#  --------
#  @quiz_bp.route("/start")
#  @student_required          ← guard runs FIRST
#  def start_quiz():
#      ...                    ← this only runs if guard passes
#
#  THREE POSSIBLE OUTCOMES when a request hits a protected route:
#  1. No token at all          → 401 Unauthorized ("please log in")
#  2. Valid token, wrong role  → 403 Forbidden    ("you can't do this")
#  3. Valid token, right role  → route function runs normally
# ============================================================

# functools.wraps preserves the name and docstring of the
# wrapped function — without it, all our routes would look
# like they're named "wrapper" in debug output
from functools import wraps

from flask import jsonify, g
# verify_jwt_in_request — checks the Authorization header
#   contains a valid, non-expired JWT token
# get_jwt_identity — extracts the user ID stored inside the token
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from models.models import User


# ── HELPER: load the current user ────────────────────────────
def _load_user():
    """
    Internal helper used by all three decorators.

    Reads the JWT token from the request header, extracts the
    user ID stored inside it, then fetches that User from the DB.

    Returns the User object, or None if something went wrong.

    NOTE: This is a private function (name starts with _) meaning
    it's only meant to be called from inside this file.
    """
    # get_jwt_identity() returns the string we passed as `identity`
    # when we called create_access_token() during login/register.
    # We stored str(user.id) there, so we convert back to int.
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


# ── DECORATOR 1: login_required ──────────────────────────────
def login_required(fn):
    """
    Allows ANY logged-in user through (student OR instructor).

    Use this for routes that both roles can access, like:
      - GET /api/auth/me       (view own profile)
      - PUT /api/auth/me       (edit own profile)

    If there's no token or the token is invalid → 401 error.
    If the user account was deleted → 404 error.
    Otherwise → route runs normally.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):

        # Step 1: Check the Authorization header has a valid token.
        # If not, flask_jwt_extended automatically raises an error
        # that Flask turns into a 401 response.
        verify_jwt_in_request()

        # Step 2: Load the User from the database
        user = _load_user()
        if not user:
            return jsonify({
                "error": "User account not found. It may have been deleted."
            }), 404

        # Step 3: Store the user on Flask's 'g' object.
        # 'g' is a special Flask object that lives for exactly one
        # request — we can store things on it and read them back
        # anywhere in the same request without querying the DB again.
        g.current_user = user

        # Step 4: All checks passed — run the actual route function
        return fn(*args, **kwargs)

    return wrapper


# ── DECORATOR 2: student_required ───────────────────────────
def student_required(fn):
    """
    Only allows users with role = 'student'.

    Use this for quiz routes, Q&A routes etc. that are
    specifically for students learning material.

    If role is 'instructor' → 403 Forbidden.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):

        verify_jwt_in_request()
        user = _load_user()

        if not user:
            return jsonify({"error": "User account not found."}), 404

        # The key check: is this user actually a student?
        if user.role != "student":
            return jsonify({
                "error": "Access denied. This route is for students only."
            }), 403  # 403 = Forbidden (you're logged in, but not allowed)

        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper


# ── DECORATOR 3: instructor_required ────────────────────────
def instructor_required(fn):
    """
    Only allows users with role = 'instructor'.

    Use this for admin routes like:
      - Listing all students
      - Viewing class-wide analytics
      - Managing the question bank

    If role is 'student' → 403 Forbidden.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):

        verify_jwt_in_request()
        user = _load_user()

        if not user:
            return jsonify({"error": "User account not found."}), 404

        if user.role != "instructor":
            return jsonify({
                "error": "Access denied. This route is for instructors only."
            }), 403

        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper


# ── HELPER: get the current user inside a route ─────────────
def get_current_user():
    """
    Returns the currently logged-in User object.

    Call this INSIDE any route that uses one of the decorators above.
    It reads the user we stored on 'g' — no extra database query needed.

    EXAMPLE:
        @auth_bp.route("/me")
        @login_required
        def get_me():
            user = get_current_user()   ← call this to get the User object
            return jsonify(user.to_dict())
    """
    return getattr(g, "current_user", None)
