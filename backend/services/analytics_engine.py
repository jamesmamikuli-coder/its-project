# ============================================================
#  services/analytics_engine.py
#  THE ANALYTICS ENGINE
#
#  This file computes all the statistics shown on the dashboards:
#
#  STUDENT DASHBOARD shows:
#    - Overall average score across all quizzes
#    - Score broken down by topic (e.g. Algorithms: 75%, DBs: 90%)
#    - Score over time (a chart of quiz scores newest→oldest)
#    - Quiz completion count and total time spent
#    - Weakest topic (where to focus next)
#    - Q&A chatbot usage stats
#
#  INSTRUCTOR DASHBOARD shows:
#    - Total students, total quizzes, class average score
#    - Per-student summary for every student
#    - At-risk students (avg < 50% and 2+ quizzes done)
#    - Top performers (avg ≥ 80%)
#    - Most-asked chatbot questions (what topics are confusing)
#    - Class-wide topic breakdown (which topics the class struggles with)
#
#  WHY A SEPARATE FILE?
#  Analytics queries are complex — they JOIN multiple tables,
#  use SQL aggregate functions (AVG, COUNT, SUM), and GROUP BY
#  fields. Keeping them here prevents routes from becoming
#  hundreds of lines long and makes the logic easier to test.
# ============================================================

import logging
from collections import Counter

from sqlalchemy import func

from extensions import db
from models.models import User, QuizAttempt, QuizAnswer, QALog, Question

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Computes all statistics for the student and instructor dashboards.
    """

    # ── STUDENT ANALYTICS ─────────────────────────────────────

    def get_student_dashboard(self, user_id):
        """
        Build a complete analytics summary for one student.

        Called when a student opens their dashboard page.

        Returns a dictionary containing everything the frontend
        needs to render charts and stats cards.

        Parameters:
            user_id (int): which student to analyse

        Returns:
            dict with all stats, or None if user doesn't exist
        """
        user = User.query.get(int(user_id))
        if not user:
            return None

        # Fetch all completed quiz attempts for this student
        # We'll reuse this list rather than querying multiple times
        attempts = (
            QuizAttempt.query
            .filter_by(user_id=user_id)
            .filter(QuizAttempt.completed_at.is_(None))
            .order_by(QuizAttempt.completed_at.asc())   # oldest first for chart
            .all()
        )

        # ── Overall stats ────────────────────────────────────
        total_quizzes  = len(attempts)
        overall_avg    = self._safe_avg([a.score for a in attempts])
        total_correct  = sum(a.correct_q for a in attempts)
        total_answered = sum(a.total_q   for a in attempts)
        total_time_secs = sum(
            a.duration_seconds for a in attempts
            if a.duration_seconds is not None
        )

        # ── Topic breakdown ───────────────────────────────────
        # Group attempts by topic and compute per-topic average
        topic_scores = self._topic_breakdown(attempts)

        # ── Weakest topic (lowest average score) ──────────────
        weakest_topic = None
        if topic_scores:
            weakest_topic = min(topic_scores, key=lambda t: t["average_score"])

        # ── Score over time (for the line chart) ──────────────
        # Each quiz attempt becomes one data point on the chart
        score_over_time = [
            {
                "attempt_number": i + 1,
                "score":          a.score,
                "topic":          a.topic,
                "difficulty":     a.difficulty,
                "date":           a.completed_at.strftime("%d %b %Y"),
            }
            for i, a in enumerate(attempts)
        ]

        # ── Difficulty distribution ───────────────────────────
        # How many quizzes did the student do at each difficulty?
        diff_counts = Counter(a.difficulty for a in attempts)
        difficulty_distribution = {
            "easy":   diff_counts.get(1, 0),
            "medium": diff_counts.get(2, 0),
            "hard":   diff_counts.get(3, 0),
        }

        # ── Q&A chatbot stats ─────────────────────────────────
        qa_logs = QALog.query.filter_by(user_id=user_id).all()
        qa_stats = self._qa_stats_for_student(qa_logs)

        # ── Recent activity (last 5 quizzes for the sidebar) ──
        recent_attempts = attempts[-5:] if len(attempts) >= 5 else attempts
        recent_attempts = list(reversed(recent_attempts))  # newest first

        return {
            "user":          user.to_dict(),
            # Overall summary cards
            "summary": {
                "total_quizzes":       total_quizzes,
                "overall_avg_score":   overall_avg,
                "total_correct":       total_correct,
                "total_answered":      total_answered,
                "total_time_minutes":  round(total_time_secs / 60, 1),
                "accuracy_pct":        round(total_correct / total_answered * 100, 1)
                                       if total_answered > 0 else 0.0,
            },
            # Data for the topic breakdown bar chart
            "topic_breakdown":         topic_scores,
            # Weakest topic callout card
            "weakest_topic":           weakest_topic,
            # Data for the score-over-time line chart
            "score_over_time":         score_over_time,
            # Difficulty distribution pie/bar chart
            "difficulty_distribution": difficulty_distribution,
            # Chatbot usage panel
            "qa_stats":                qa_stats,
            # Recent activity list
            "recent_attempts": [a.to_dict() for a in recent_attempts],
        }

    def _topic_breakdown(self, attempts):
        """
        Given a list of QuizAttempt objects, group by topic and
        calculate the average score and attempt count per topic.

        Returns a list of dicts, sorted by average_score ascending
        (worst topic first — easier to spot where help is needed).

        Example return:
        [
            {"topic": "Databases",       "average_score": 55.0, "attempts": 2},
            {"topic": "Algorithms",      "average_score": 72.0, "attempts": 4},
            {"topic": "Data Structures", "average_score": 88.0, "attempts": 3},
        ]
        """
        # Group attempts by topic using a plain dictionary
        topic_data = {}
        for a in attempts:
            if a.topic not in topic_data:
                topic_data[a.topic] = []
            topic_data[a.topic].append(a.score)

        result = []
        for topic, scores in topic_data.items():
            result.append({
                "topic":         topic,
                "average_score": self._safe_avg(scores),
                "attempts":      len(scores),
            })

        # Sort worst first so the chart highlights weak areas
        result.sort(key=lambda x: x["average_score"])
        return result

    def _qa_stats_for_student(self, qa_logs):
        """
        Summarize a student's chatbot usage.

        Returns:
        {
            "total_questions_asked": 8,
            "helpful_count":         5,
            "not_helpful_count":     1,
            "no_feedback_count":     2,
            "most_asked_topic":      "Data Structures"
        }
        """
        total = len(qa_logs)
        helpful     = sum(1 for l in qa_logs if l.was_helpful is True)
        not_helpful = sum(1 for l in qa_logs if l.was_helpful is False)
        no_feedback = total - helpful - not_helpful

        # Find the topic they asked about most
        topics = [l.matched_topic for l in qa_logs if l.matched_topic]
        most_asked = Counter(topics).most_common(1)
        most_asked_topic = most_asked[0][0] if most_asked else None

        return {
            "total_questions_asked": total,
            "helpful_count":         helpful,
            "not_helpful_count":     not_helpful,
            "no_feedback_count":     no_feedback,
            "most_asked_topic":      most_asked_topic,
        }

    # ── INSTRUCTOR ANALYTICS ──────────────────────────────────

    def get_instructor_dashboard(self):
        """
        Build the class-wide analytics summary for the instructor.

        This is the most data-rich endpoint — it covers all students,
        all quizzes, and all chatbot interactions.

        Returns a large dictionary with everything the instructor
        dashboard needs.
        """
        # ── Class-wide quiz stats ─────────────────────────────
        all_students = (
            User.query
            .filter_by(role="student")
            .order_by(User.created_at.desc())
            .all()
        )

        all_completed = (
            QuizAttempt.query
            .filter(QuizAttempt.completed_at.is_(None))
            .all()
        )

        total_students    = len(all_students)
        total_quizzes     = len(all_completed)
        class_avg         = self._safe_avg([a.score for a in all_completed])

        # ── Per-student summaries ─────────────────────────────
        student_summaries = []
        at_risk           = []
        top_performers    = []

        for student in all_students:
            summary = self._student_summary(student, all_completed)
            student_summaries.append(summary)

            if summary["is_at_risk"]:
                at_risk.append(summary)

            if summary["total_quizzes"] > 0 and summary["average_score"] >= 80:
                top_performers.append(summary)

        # Sort at-risk by worst score first (most urgent at the top)
        at_risk.sort(key=lambda x: x["average_score"])
        # Sort top performers by best score first
        top_performers.sort(key=lambda x: -x["average_score"])

        # ── Class topic breakdown ─────────────────────────────
        class_topic_breakdown = self._class_topic_breakdown(all_completed)

        # ── Difficulty distribution across the whole class ────
        diff_counts = Counter(a.difficulty for a in all_completed)
        difficulty_distribution = {
            "easy":   diff_counts.get(1, 0),
            "medium": diff_counts.get(2, 0),
            "hard":   diff_counts.get(3, 0),
        }

        # ── Chatbot analytics ─────────────────────────────────
        qa_analytics = self._class_qa_analytics()

        # ── Score trend over time (for a class-wide chart) ────
        # Group all completed attempts by week and average the scores
        score_trend = self._class_score_trend(all_completed)

        return {
            # Summary cards at the top of the dashboard
            "summary": {
                "total_students":   total_students,
                "total_quizzes":    total_quizzes,
                "class_avg_score":  class_avg,
                "at_risk_count":    len(at_risk),
                "top_performer_count": len(top_performers),
            },
            # Full list of student rows in the table
            "students":                 student_summaries,
            # Highlighted sections
            "at_risk_students":         at_risk,
            "top_performers":           top_performers,
            # Charts
            "class_topic_breakdown":    class_topic_breakdown,
            "difficulty_distribution":  difficulty_distribution,
            "score_trend":              score_trend,
            # Chatbot panel
            "qa_analytics":             qa_analytics,
        }

    def _student_summary(self, student, all_completed):
        """
        Build a summary dict for one student.
        Uses the pre-fetched list of all completed attempts
        so we don't make a separate DB query per student.
        """
        # Filter from the already-fetched list (no extra DB hit)
        student_attempts = [a for a in all_completed if a.user_id == student.id]

        total_quizzes = len(student_attempts)
        average_score = self._safe_avg([a.score for a in student_attempts])
        qa_count      = QALog.query.filter_by(user_id=student.id).count()

        # At-risk: average below 50% AND has done at least 2 quizzes
        # (we need at least 2 quizzes to make a fair judgement)
        is_at_risk = average_score < 50 and total_quizzes >= 2

        return {
            "user":          student.to_dict(),
            "total_quizzes": total_quizzes,
            "average_score": average_score,
            "qa_count":      qa_count,
            "is_at_risk":    is_at_risk,
        }

    def _class_topic_breakdown(self, all_completed):
        """
        Compute average scores per topic across ALL students.

        This tells the instructor which topics the whole class
        is struggling with, not just individual students.

        Returns list sorted worst topic first:
        [
            {"topic": "Algorithms",      "average_score": 58.0, "attempts": 23},
            {"topic": "Data Structures", "average_score": 71.0, "attempts": 31},
            ...
        ]
        """
        topic_data = {}
        for a in all_completed:
            if a.topic not in topic_data:
                topic_data[a.topic] = []
            topic_data[a.topic].append(a.score)

        result = [
            {
                "topic":         topic,
                "average_score": self._safe_avg(scores),
                "attempts":      len(scores),
            }
            for topic, scores in topic_data.items()
        ]
        result.sort(key=lambda x: x["average_score"])
        return result

    def _class_qa_analytics(self):
        """
        Analyse all chatbot interactions across the whole class.

        Returns:
        {
            "total_questions_asked": 47,
            "helpful_rate_pct":      68.0,
            "top_topics": [
                {"topic": "Data Structures", "count": 18},
                {"topic": "Algorithms",      "count": 14},
                ...
            ],
            "unanswered_count": 5,
            "recent_questions": [
                {"question": "What is a queue?", "asked_at": "..."},
                ...
            ]
        }
        """
        all_logs = QALog.query.order_by(QALog.asked_at.desc()).all()
        total    = len(all_logs)

        # Helpful rate: of logs that have feedback, what % were helpful?
        with_feedback = [l for l in all_logs if l.was_helpful is not None]
        helpful       = sum(1 for l in with_feedback if l.was_helpful)
        helpful_rate  = round(helpful / len(with_feedback) * 100, 1) if with_feedback else 0.0

        # Top topics students ask about
        topic_counter = Counter(
            l.matched_topic for l in all_logs if l.matched_topic
        )
        top_topics = [
            {"topic": topic, "count": count}
            for topic, count in topic_counter.most_common(5)
        ]

        # Questions the engine couldn't answer (found=False)
        # Confidence=0 means the engine said "I don't know"
        unanswered = sum(1 for l in all_logs if l.confidence == 0.0)

        # Most recent 10 questions (for the instructor to see trends)
        recent = [
            {
                "question":      l.question,
                "matched_topic": l.matched_topic,
                "was_helpful":   l.was_helpful,
                "asked_at":      l.asked_at.isoformat(),
            }
            for l in all_logs[:10]
        ]

        return {
            "total_questions_asked": total,
            "helpful_rate_pct":      helpful_rate,
            "top_topics":            top_topics,
            "unanswered_count":      unanswered,
            "recent_questions":      recent,
        }

    def _class_score_trend(self, all_completed):
        """
        Build a weekly score trend for the class-wide line chart.

        Groups quiz attempts by the week they were completed and
        computes the average score for that week.

        Returns a list of data points ordered oldest→newest:
        [
            {"week": "06 Jan 2025", "average_score": 63.0, "count": 4},
            {"week": "13 Jan 2025", "average_score": 68.5, "count": 7},
            ...
        ]
        """
        if not all_completed:
            return []

        # Group by week using Python's isocalendar()
        # isocalendar() returns (year, week_number, weekday)
        weekly = {}
        for a in all_completed:
            year, week, _ = a.completed_at.isocalendar()
            key = (year, week)
            if key not in weekly:
                weekly[key] = []
            weekly[key].append(a.score)

        result = []
        for (year, week), scores in sorted(weekly.items()):
            # Calculate the Monday date of that week for a readable label
            import datetime
            monday = datetime.datetime.fromisocalendar(year, week, 1)
            result.append({
                "week":          monday.strftime("%d %b %Y"),
                "average_score": self._safe_avg(scores),
                "count":         len(scores),
            })

        return result

    # ── INDIVIDUAL STUDENT DETAIL (for instructor) ────────────

    def get_student_detail(self, student_id):
        """
        Get the full analytics for ONE student, for the instructor
        to view on a student detail page.

        Parameters:
            student_id (int): the student's user ID

        Returns:
            The same format as get_student_dashboard(), or None
            if the student doesn't exist or isn't a student.
        """
        student = User.query.get(int(student_id))

        if not student or student.role != "student":
            return None

        # Reuse the student dashboard logic
        return self.get_student_dashboard(student_id)

    # ── SHARED HELPERS ────────────────────────────────────────

    def _safe_avg(self, values):
        """
        Safely compute the average of a list of numbers.
        Returns 0.0 if the list is empty (avoids ZeroDivisionError).

        Example:
            _safe_avg([80, 60, 70])  →  70.0
            _safe_avg([])            →  0.0
        """
        if not values:
            return 0.0
        return round(sum(values) / len(values), 1)


# ── Global engine instance ────────────────────────────────────
analytics_engine = AnalyticsEngine()
