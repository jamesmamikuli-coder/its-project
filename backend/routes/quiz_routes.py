# ============================================================
#  routes/quiz_routes.py
#  ADAPTIVE QUIZ API ENDPOINTS
#
#  These routes let students start quizzes, submit answers,
#  and review their past performance.
#
#  ENDPOINTS:
#  ┌────────┬──────────────────────────────┬──────────────────────────────┐
#  │ METHOD │ URL                          │ What it does                 │
#  ├────────┼──────────────────────────────┼──────────────────────────────┤
#  │ GET    │ /api/quiz/topics             │ List all available topics    │
#  │ GET    │ /api/quiz/start              │ Start a new adaptive quiz    │
#  │ POST   │ /api/quiz/submit             │ Submit answers, get score    │
#  │ GET    │ /api/quiz/history            │ My past quiz attempts        │
#  │ GET    │ /api/quiz/attempt/<id>       │ Full detail of one attempt   │
#  └────────┴──────────────────────────────┴──────────────────────────────┘
#
#  ALL routes require a JWT token.
#  Students can only access their own quiz data.
# ============================================================

import logging

from flask import Blueprint, request, jsonify

from middleware.auth_middleware import login_required, get_current_user
from services.quiz_engine import quiz_engine

logger   = logging.getLogger(__name__)
quiz_bp  = Blueprint("quiz", __name__)


# ============================================================
#  ENDPOINT 1: GET /api/quiz/topics
#  Returns all topics a student can be quizzed on
# ============================================================
@quiz_bp.route("/topics", methods=["GET"])
@login_required
def get_topics():
    """
    Returns the list of all available quiz topics.

    The frontend uses this to populate the topic selection
    dropdown on the quiz page.

    RESPONSE:
    {
        "topics": [
            "Algorithms",
            "Data Structures",
            "Databases",
            "Programming Concepts"
        ]
    }
    """
    topics = quiz_engine.get_available_topics()

    return jsonify({"topics": topics}), 200


# ============================================================
#  ENDPOINT 2: GET /api/quiz/start
#  Start a new adaptive quiz
# ============================================================
@quiz_bp.route("/start", methods=["GET"])
@login_required
def start_quiz():
    """
    Generate a new quiz for the logged-in student.

    The difficulty is chosen AUTOMATICALLY based on how the
    student has performed in previous quizzes on this topic.
    They don't need to choose a difficulty — the system adapts.

    REQUIRED URL parameter:
        ?topic=Algorithms

    OPTIONAL URL parameter:
        ?count=5     (number of questions, default is 5)

    RESPONSE (success):
    {
        "attempt_id":        7,
        "topic":             "Algorithms",
        "difficulty":        2,
        "difficulty_label":  "Medium",
        "total_questions":   5,
        "questions": [
            {
                "id":            9,
                "topic":         "Algorithms",
                "subtopic":      "Sorting",
                "question_text": "Which sorting algorithm works by...",
                "option_a":      "Quick Sort",
                "option_b":      "Heap Sort",
                "option_c":      "Insertion Sort",
                "option_d":      "Merge Sort",
                "difficulty":    2
                ← NOTE: correct_answer is NOT included here!
            },
            ...
        ]
    }

    RESPONSE (error — invalid topic):
    {
        "error": "Topic 'Xyz' not found. Available topics: ..."
    }
    """
    user = get_current_user()

    # ── Read and validate the topic parameter ─────────────────
    topic = request.args.get("topic", "").strip()

    if not topic:
        # No topic given — tell them what topics are available
        available = quiz_engine.get_available_topics()
        return jsonify({
            "error":             "Please provide a topic using ?topic=TopicName",
            "available_topics":  available,
        }), 400

    # Check the topic actually exists in the question bank
    available_topics = quiz_engine.get_available_topics()
    # Case-insensitive check
    matched_topic = next(
        (t for t in available_topics if t.lower() == topic.lower()),
        None
    )

    if not matched_topic:
        return jsonify({
            "error":            f"Topic '{topic}' not found in the question bank.",
            "available_topics": available_topics,
        }), 404

    # ── Start the quiz ────────────────────────────────────────
    # quiz_engine.start_quiz() handles:
    #   1. Determining the right difficulty for this student
    #   2. Selecting random questions
    #   3. Creating a QuizAttempt record in the database
    result = quiz_engine.start_quiz(
        user_id = user.id,
        topic   = matched_topic,
    )

    if not result:
        return jsonify({
            "error": f"No questions available for topic '{matched_topic}'. "
                     f"Please run seed_data.py to add questions."
        }), 404

    logger.info(
        f"Quiz started: user={user.id} topic={matched_topic} "
        f"difficulty={result['difficulty']} attempt={result['attempt_id']}"
    )

    return jsonify(result), 200


# ============================================================
#  ENDPOINT 3: POST /api/quiz/submit
#  Submit completed quiz answers and receive a score
# ============================================================
@quiz_bp.route("/submit", methods=["POST"])
@login_required
def submit_quiz():
    """
    Submit a completed quiz and receive:
      - Overall score (percentage)
      - Which questions were right/wrong
      - Explanation for each question
      - Encouraging feedback message
      - What difficulty to expect next time

    REQUEST BODY (JSON):
    {
        "attempt_id": 7,
        "answers": [
            {
                "question_id":     9,
                "selected_answer": "D",
                "time_taken_secs": 18
            },
            {
                "question_id":     12,
                "selected_answer": "A",
                "time_taken_secs": 8
            },
            ...
        ]
    }

    RESPONSE:
    {
        "attempt_id":        7,
        "score":             80.0,
        "correct_q":         4,
        "total_q":           5,
        "topic":             "Algorithms",
        "difficulty":        2,
        "difficulty_label":  "Medium",
        "feedback_message":  "🌟 Excellent! You have a strong grasp...",
        "next_difficulty":   3,
        "next_difficulty_label": "Hard",
        "duration_seconds":  127,
        "answers": [
            {
                "question_id":     9,
                "question_text":   "Which sorting algorithm...",
                "selected_answer": "D",
                "correct_answer":  "D",
                "is_correct":      true,
                "explanation":     "Merge Sort is a divide-and-conquer...",
                "topic":           "Algorithms",
                "time_taken_secs": 18
            },
            ...
        ]
    }
    """
    user = get_current_user()
    data = request.get_json()

    # ── Validate the request body ──────────────────────────────
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    attempt_id   = data.get("attempt_id")
    answers_data = data.get("answers", [])

    if not attempt_id:
        return jsonify({"error": "'attempt_id' is required."}), 400

    if not answers_data:
        return jsonify({"error": "'answers' list is required and cannot be empty."}), 400

    if not isinstance(answers_data, list):
        return jsonify({"error": "'answers' must be a list."}), 400

    # Validate each answer entry has required fields
    for i, ans in enumerate(answers_data):
        if "question_id" not in ans:
            return jsonify({
                "error": f"Answer at index {i} is missing 'question_id'."
            }), 400
        if "selected_answer" not in ans:
            return jsonify({
                "error": f"Answer at index {i} is missing 'selected_answer'."
            }), 400

    # ── Score and save the quiz ────────────────────────────────
    result = quiz_engine.submit_quiz(
        attempt_id   = attempt_id,
        user_id      = user.id,
        answers_data = answers_data,
    )

    # submit_quiz returns None if attempt not found or already submitted
    if result is None:
        return jsonify({
            "error": "Quiz attempt not found, does not belong to you, "
                     "or has already been submitted."
        }), 404

    logger.info(
        f"Quiz submitted: user={user.id} attempt={attempt_id} "
        f"score={result['score']}%"
    )

    return jsonify(result), 200


# ============================================================
#  ENDPOINT 4: GET /api/quiz/history
#  Get the student's past completed quizzes
# ============================================================
@quiz_bp.route("/history", methods=["GET"])
@login_required
def get_history():
    """
    Returns the logged-in student's quiz history, newest first.

    Optional URL parameter:
        ?limit=20    → how many records to return (default: 20)

    RESPONSE:
    {
        "history": [
            {
                "id":               7,
                "user_id":          3,
                "topic":            "Algorithms",
                "score":            80.0,
                "correct_q":        4,
                "total_q":          5,
                "difficulty":       2,
                "is_completed":     true,
                "duration_seconds": 127,
                "started_at":       "2024-01-15T10:30:00",
                "completed_at":     "2024-01-15T10:32:07"
            },
            ...
        ],
        "total": 3
    }
    """
    user = get_current_user()

    try:
        limit = int(request.args.get("limit", 20))
        limit = max(1, min(limit, 100))
    except ValueError:
        limit = 20

    history = quiz_engine.get_quiz_history(user_id=user.id, limit=limit)

    return jsonify({
        "history": [attempt.to_dict() for attempt in history],
        "total":   len(history),
    }), 200


# ============================================================
#  ENDPOINT 5: GET /api/quiz/attempt/<id>
#  Get the full detail of one specific quiz attempt
# ============================================================
@quiz_bp.route("/attempt/<int:attempt_id>", methods=["GET"])
@login_required
def get_attempt_detail(attempt_id):
    """
    Returns full detail of one quiz attempt, including:
      - The overall score
      - Every question with the student's answer
      - Whether each answer was correct
      - The explanation for each question

    Used on the "Review Quiz" page so students can learn
    from their mistakes after the quiz.

    URL example: GET /api/quiz/attempt/7

    RESPONSE:
    {
        "id":               7,
        "topic":            "Algorithms",
        "score":            80.0,
        "difficulty":       2,
        "difficulty_label": "Medium",
        "answers": [
            {
                "question_id":     9,
                "question_text":   "Which sorting algorithm...",
                "selected_answer": "D",
                "correct_answer":  "D",
                "is_correct":      true,
                "explanation":     "Merge Sort is a divide-and-conquer...",
                "time_taken_secs": 18
            },
            ...
        ]
    }
    """
    user = get_current_user()

    detail = quiz_engine.get_attempt_detail(
        attempt_id = attempt_id,
        user_id    = user.id,
    )

    if not detail:
        return jsonify({
            "error": f"Quiz attempt {attempt_id} not found, not completed, "
                     f"or does not belong to you."
        }), 404

    return jsonify(detail), 200
