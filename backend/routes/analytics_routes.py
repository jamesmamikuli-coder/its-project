# ============================================================
#  routes/analytics_routes.py
#  ANALYTICS DASHBOARD API ENDPOINTS
#
#  These routes serve all the data for the dashboards.
#
#  ENDPOINTS:
#  ┌────────┬──────────────────────────────────┬─────────────────────────────┐
#  │ METHOD │ URL                              │ Who  │ What it does          │
#  ├────────┼──────────────────────────────────┼──────┼───────────────────────┤
#  │ GET    │ /api/analytics/student/me        │ Stu  │ My own dashboard data │
#  │ GET    │ /api/analytics/instructor        │ Inst │ Class-wide overview   │
#  │ GET    │ /api/analytics/student/<id>      │ Inst │ One student's detail  │
#  │ GET    │ /api/analytics/leaderboard       │ Both │ Top 10 students       │
#  └────────┴──────────────────────────────────┴──────┴───────────────────────┘
# ============================================================

import logging

from flask import Blueprint, jsonify, request

from middleware.auth_middleware import (
    login_required,
    instructor_required,
    get_current_user,
)
from services.analytics_engine import analytics_engine
from models.models import User, QuizAttempt

logger       = logging.getLogger(__name__)
analytics_bp = Blueprint("analytics", __name__)


# ============================================================
#  ENDPOINT 1: GET /api/analytics/student/me
#  Returns the logged-in student's full dashboard data
# ============================================================
@analytics_bp.route("/student/me", methods=["GET"])
@login_required
def get_my_dashboard():
    """
    Returns everything the student dashboard needs to render:
      - Summary cards (total quizzes, avg score, time spent)
      - Topic breakdown (bar chart data)
      - Score over time (line chart data)
      - Difficulty distribution (pie chart data)
      - Weakest topic (focus recommendation)
      - Chatbot usage stats
      - Recent quiz attempts

    RESPONSE SHAPE:
    {
        "user": { ... },
        "summary": {
            "total_quizzes":      12,
            "overall_avg_score":  68.5,
            "total_correct":      42,
            "total_answered":     60,
            "total_time_minutes": 24.3,
            "accuracy_pct":       70.0
        },
        "topic_breakdown": [
            { "topic": "Algorithms",      "average_score": 55.0, "attempts": 4 },
            { "topic": "Data Structures", "average_score": 72.0, "attempts": 5 },
            { "topic": "Databases",       "average_score": 85.0, "attempts": 3 }
        ],
        "weakest_topic": {
            "topic": "Algorithms", "average_score": 55.0, "attempts": 4
        },
        "score_over_time": [
            { "attempt_number": 1, "score": 60.0, "topic": "Algorithms", "date": "01 Jan 2025" },
            { "attempt_number": 2, "score": 80.0, "topic": "Databases",  "date": "03 Jan 2025" },
            ...
        ],
        "difficulty_distribution": { "easy": 5, "medium": 5, "hard": 2 },
        "qa_stats": {
            "total_questions_asked": 8,
            "helpful_count": 5,
            "most_asked_topic": "Data Structures"
        },
        "recent_attempts": [ { attempt dict }, ... ]
    }
    """
    user = get_current_user()
    data = analytics_engine.get_student_dashboard(user.id)

    if not data:
        return jsonify({"error": "Could not load dashboard data."}), 500

    return jsonify(data), 200


# ============================================================
#  ENDPOINT 2: GET /api/analytics/instructor
#  Returns the class-wide analytics for the instructor
# ============================================================
@analytics_bp.route("/instructor", methods=["GET"])
@instructor_required
def get_instructor_dashboard():
    """
    Returns everything the instructor dashboard needs:
      - Class summary cards
      - Per-student summary table
      - At-risk students (avg < 50%, 2+ quizzes)
      - Top performers (avg ≥ 80%)
      - Class-wide topic breakdown
      - Difficulty distribution
      - Weekly score trend
      - Chatbot analytics

    RESPONSE SHAPE:
    {
        "summary": {
            "total_students":      25,
            "total_quizzes":       143,
            "class_avg_score":     68.4,
            "at_risk_count":       4,
            "top_performer_count": 7
        },
        "students": [
            {
                "user":          { user dict },
                "total_quizzes": 8,
                "average_score": 72.5,
                "qa_count":      3,
                "is_at_risk":    false
            },
            ...
        ],
        "at_risk_students":      [ ... ],
        "top_performers":        [ ... ],
        "class_topic_breakdown": [
            { "topic": "Algorithms", "average_score": 58.0, "attempts": 47 },
            ...
        ],
        "difficulty_distribution": { "easy": 60, "medium": 55, "hard": 28 },
        "score_trend": [
            { "week": "06 Jan 2025", "average_score": 63.0, "count": 4 },
            ...
        ],
        "qa_analytics": {
            "total_questions_asked": 47,
            "helpful_rate_pct":      68.0,
            "top_topics":            [ { "topic": "...", "count": 18 }, ... ],
            "unanswered_count":      5,
            "recent_questions":      [ ... ]
        }
    }
    """
    data = analytics_engine.get_instructor_dashboard()
    return jsonify(data), 200


# ============================================================
#  ENDPOINT 3: GET /api/analytics/student/<id>
#  Instructor views one specific student's dashboard
# ============================================================
@analytics_bp.route("/student/<int:student_id>", methods=["GET"])
@instructor_required
def get_student_detail(student_id):
    """
    Returns the full analytics for one specific student.
    Only instructors can view other students' data.

    URL example: GET /api/analytics/student/5

    Returns the same shape as /student/me (above).
    """
    data = analytics_engine.get_student_detail(student_id)

    if not data:
        return jsonify({
            "error": f"Student with ID {student_id} not found "
                     f"or is not a student account."
        }), 404

    return jsonify(data), 200


# ============================================================
#  ENDPOINT 4: GET /api/analytics/leaderboard
#  Top 10 students by average score
# ============================================================
@analytics_bp.route("/leaderboard", methods=["GET"])
@login_required
def get_leaderboard():
    """
    Returns the top students ranked by average quiz score.
    Both students and instructors can view this.

    Only students who have completed at least 2 quizzes are
    included (to ensure the ranking is meaningful).

    Optional URL parameter:
        ?limit=10    → how many students to show (default: 10)

    RESPONSE:
    {
        "leaderboard": [
            {
                "rank":          1,
                "name":          "Amina Bello",
                "average_score": 92.0,
                "total_quizzes": 8,
                "badge":         "🏆"
            },
            {
                "rank":          2,
                "name":          "Kwame Osei",
                "average_score": 87.5,
                "total_quizzes": 6,
                "badge":         "🥈"
            },
            ...
        ],
        "total_eligible": 18
    }
    """
    try:
        limit = int(request.args.get("limit", 10))
        limit = max(1, min(limit, 50))
    except ValueError:
        limit = 10

    # Get all students
    students = User.query.filter_by(role="student").all()

    # Build ranked list — only include students with 2+ completed quizzes
    ranked = []
    for student in students:
        attempts = (
            QuizAttempt.query
            .filter_by(user_id=student.id)
            .filter(QuizAttempt.completed_at.isnot(None))
            .all()
        )
        # Require at least 2 quizzes to appear in the leaderboard
        if len(attempts) < 2:
            continue

        avg = round(sum(a.score for a in attempts) / len(attempts), 1)
        ranked.append({
            "name":          student.name,
            "average_score": avg,
            "total_quizzes": len(attempts),
        })

    # Sort by average score descending (best first)
    ranked.sort(key=lambda x: -x["average_score"])

    # Take only the top N and add rank numbers + badges
    badges = {1: "🏆", 2: "🥈", 3: "🥉"}
    leaderboard = []
    for i, entry in enumerate(ranked[:limit]):
        leaderboard.append({
            "rank":          i + 1,
            "name":          entry["name"],
            "average_score": entry["average_score"],
            "total_quizzes": entry["total_quizzes"],
            # Trophy for 1st, silver for 2nd, bronze for 3rd, star for rest
            "badge":         badges.get(i + 1, "⭐"),
        })

    return jsonify({
        "leaderboard":    leaderboard,
        "total_eligible": len(ranked),
    }), 200
