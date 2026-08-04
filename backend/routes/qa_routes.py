# ============================================================
#  routes/qa_routes.py
#  Q&A CHATBOT API ENDPOINTS
#
#  These routes connect the React frontend chatbot UI to our
#  NLP engine (services/qa_engine.py).
#
#  ENDPOINTS:
#  ┌────────┬──────────────────────────┬──────────────────────────────┐
#  │ METHOD │ URL                      │ What it does                 │
#  ├────────┼──────────────────────────┼──────────────────────────────┤
#  │ POST   │ /api/qa/ask              │ Submit a question, get answer│
#  │ GET    │ /api/qa/history          │ Get my past Q&A conversations│
#  │ POST   │ /api/qa/feedback         │ Rate an answer helpful/not   │
#  │ GET    │ /api/qa/suggestions      │ Get sample questions to ask  │
#  └────────┴──────────────────────────┴──────────────────────────────┘
#
#  ALL routes require a JWT token (student or instructor).
# ============================================================

import logging

from flask import Blueprint, request, jsonify

from extensions import db 
from middleware.auth_middleware import login_required, get_current_user
from models.models import KnowledgeArticle, QALog
from services.qa_engine import qa_engine

logger = logging.getLogger(__name__)
qa_bp  = Blueprint("qa", __name__)


# ============================================================
#  ENGINE INITIALISATION
#  Called once when Flask starts — trains the NLP engine
# ============================================================
def init_qa_engine(app):
    """
    Load knowledge articles from the database and fit the QA engine.

    This is called in app.py inside the app_context block so
    the engine is trained and ready before any student asks a question.
    """
    with app.app_context():
        articles = KnowledgeArticle.query.all()

        if not articles:
            print("⚠️  No knowledge articles found. Run: python seed_data.py")
            return

        qa_engine.fit(articles)
        print(f"🤖 QA Engine ready — {len(articles)} knowledge articles loaded.")


# ============================================================
#  ENDPOINT 1: POST /api/qa/ask
#  The student sends a question and we return the best answer
# ============================================================
@qa_bp.route("/ask", methods=["POST"])
@login_required
def ask_question():
    """
    Receive a student's question, search the knowledge base,
    save the interaction, and return the answer.

    REQUEST BODY (JSON):
    {
        "question": "What is a linked list?"
    }

    SUCCESS RESPONSE:
    {
        "found":      true,
        "answer":     "A linked list is a linear data structure...",
        "title":      "What is a Linked List?",
        "topic":      "Data Structures",
        "confidence": 0.73,
        "log_id":     42
    }

    NO MATCH RESPONSE:
    {
        "found":      false,
        "answer":     "I couldn't find a good answer to that...",
        "title":      null,
        "topic":      null,
        "confidence": 0.0,
        "log_id":     43
    }
    """
    user = get_current_user()
    data = request.get_json()

    # ── Validate ─────────────────────────────────────────────
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    question_text = data.get("question", "").strip()

    if not question_text:
        return jsonify({"error": "Please provide a question."}), 400

    if len(question_text) > 500:
        return jsonify({"error": "Question too long — keep it under 500 characters."}), 400

    # ── Run the NLP engine ───────────────────────────────────
    # qa_engine.answer() does the TF-IDF search and returns the best match
    result = qa_engine.answer(question_text)

    # ── Log to database ──────────────────────────────────────
    # Every Q&A exchange is saved so instructors can see in analytics
    # what topics students are struggling with
    log_entry = QALog(
        user_id       = user.id,
        question      = question_text,
        answer        = result["answer"],
        matched_topic = result.get("topic"),
        confidence    = result.get("confidence", 0.0),
    )
    db.session.add(log_entry)
    db.session.commit()

    # ── Respond ──────────────────────────────────────────────
    return jsonify({
        "found":      result["found"],
        "answer":     result["answer"],
        "title":      result.get("title"),
        "topic":      result.get("topic"),
        "confidence": result.get("confidence", 0.0),
        "log_id":     log_entry.id,
    }), 200


# ============================================================
#  ENDPOINT 2: GET /api/qa/history
#  Returns the student's past Q&A conversations
# ============================================================
@qa_bp.route("/history", methods=["GET"])
@login_required
def get_history():
    """
    Returns the logged-in user's chatbot history, newest first.

    Optional URL parameter:
        ?limit=20    → how many records to return (default: 20)

    RESPONSE:
    {
        "history": [
            {
                "id":            42,
                "question":      "What is a linked list?",
                "answer":        "A linked list is...",
                "matched_topic": "Data Structures",
                "confidence":    0.73,
                "was_helpful":   null,
                "asked_at":      "2024-01-15T10:30:00"
            }
        ],
        "total": 1
    }
    """
    user = get_current_user()

    # Read the optional ?limit= URL parameter
    try:
        limit = int(request.args.get("limit", 20))
        limit = max(1, min(limit, 100))   # clamp between 1 and 100
    except ValueError:
        limit = 20

    logs = (
        QALog.query
        .filter_by(user_id=user.id)
        .order_by(QALog.asked_at.desc())
        .limit(limit)
        .all()
    )

    return jsonify({
        "history": [log.to_dict() for log in logs],
        "total":   len(logs),
    }), 200


# ============================================================
#  ENDPOINT 3: POST /api/qa/feedback
#  Rate whether an answer was helpful
# ============================================================
@qa_bp.route("/feedback", methods=["POST"])
@login_required
def submit_feedback():
    """
    Mark a Q&A log entry as helpful or not helpful.

    REQUEST BODY:
    {
        "log_id":      42,
        "was_helpful": true
    }

    was_helpful: true  = student found the answer useful
    was_helpful: false = student did not find it useful
    """
    user = get_current_user()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    log_id      = data.get("log_id")
    was_helpful = data.get("was_helpful")

    if log_id is None:
        return jsonify({"error": "log_id is required."}), 400

    if not isinstance(was_helpful, bool):
        return jsonify({"error": "was_helpful must be true or false."}), 400

    # Find log — verify it belongs to this user (security check)
    log_entry = QALog.query.filter_by(id=log_id, user_id=user.id).first()

    if not log_entry:
        return jsonify({"error": "Log entry not found or does not belong to you."}), 404

    log_entry.was_helpful = was_helpful
    db.session.commit()

    return jsonify({"message": "Thank you for your feedback!"}), 200


# ============================================================
#  ENDPOINT 4: GET /api/qa/suggestions
#  Returns sample questions the student can click to ask
# ============================================================
@qa_bp.route("/suggestions", methods=["GET"])
@login_required
def get_suggestions():
    """
    Returns example questions for the chatbot UI.

    Optional URL parameter:
        ?topic=Data Structures    → topic-specific suggestions

    RESPONSE:
    {
        "suggestions": [
            "What is a linked list?",
            "How does a stack work?",
            ...
        ]
    }
    """
    topic = request.args.get("topic")
    suggestions = qa_engine.get_suggestions(topic=topic)

    return jsonify({"suggestions": suggestions}), 200
