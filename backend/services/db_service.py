# ============================================================
#  services/db_service.py
#  REUSABLE DATABASE HELPER FUNCTIONS
#
#  WHY DOES THIS FILE EXIST?
#  ─────────────────────────
#  Without this file, every route would have to write the same
#  database queries over and over again. For example, "get a
#  student's average score" might be needed in the quiz route,
#  the analytics route, AND the instructor dashboard.
#
#  Instead of copying that code three times, we write it ONCE
#  here and all three routes just call the function.
#
#  This is a programming principle called DRY:
#  Don't Repeat Yourself.
#
#  HOW THIS FILE IS ORGANISED:
#  ────────────────────────────
#  UserService  — functions about users and their accounts
#  QuizService  — functions about quizzes, scores, difficulty
#
#  HOW TO USE IN A ROUTE FILE:
#  ────────────────────────────
#  from services.db_service import UserService, QuizService
#
#  Then call like:
#  summary = UserService.get_student_summary(user_id=5)
#  level   = QuizService.determine_difficulty(user_id=5, topic="Algorithms")
# ============================================================

from extentions import db
from models.models import User, QuizAttempt, Question, QALog
from sqlalchemy import func


class UserService:
    """
    Helper functions for User-related database queries.

    All methods are @staticmethod which means you call them as:
        UserService.get_by_id(5)
    You do NOT need to create an instance: UserService() first.
    """

    @staticmethod
    def get_by_id(user_id):
        """
        Fetch a single User by their ID.
        Returns the User object, or None if not found.

        Example:
            user = UserService.get_by_id(3)
            if user:
                print(user.name)
        """
        return User.query.get(int(user_id))

    @staticmethod
    def get_by_email(email):
        """
        Fetch a User by email address.
        Emails are stored lowercase so we lowercase the input too.
        """
        return User.query.filter_by(email=email.lower().strip()).first()

    @staticmethod
    def get_all_students():
        """
        Return all users with role='student', newest first.
        Used by the instructor dashboard.
        """
        return (
            User.query
            .filter_by(role="student")
            .order_by(User.created_at.desc())
            .all()
        )

    @staticmethod
    def get_student_summary(user_id):
        """
        Build a complete performance summary for one student.
        Used when an instructor clicks on a student's profile.

        Returns a dictionary:
        {
            "user":                  { ...user data... },
            "total_quizzes":         8,
            "average_score":         72.5,
            "total_questions_asked": 15,
            "is_at_risk":            False
        }
        Returns None if user doesn't exist.
        """
        user = User.query.get(int(user_id))
        if not user:
            return None

        # COUNT(*) in SQL — count completed quiz attempts
        total_quizzes = (
            QuizAttempt.query
            .filter_by(user_id=user_id)
            .filter(QuizAttempt.completed_at.isnot(None))
            .count()
        )

        # AVG() in SQL — average score of all completed quizzes
        # .scalar() returns just the single value (or None if no rows)
        avg_result = (
            db.session.query(func.avg(QuizAttempt.score))
            .filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.completed_at.isnot(None)
            )
            .scalar()
        )
        average_score = round(float(avg_result), 1) if avg_result else 0.0

        # Count chatbot questions asked
        questions_asked = QALog.query.filter_by(user_id=user_id).count()

        # At-risk = done 2+ quizzes but averaging below 50%
        is_at_risk = (total_quizzes >= 2 and average_score < 50.0)

        return {
            "user":                  user.to_dict(),
            "total_quizzes":         total_quizzes,
            "average_score":         average_score,
            "total_questions_asked": questions_asked,
            "is_at_risk":            is_at_risk
        }

    @staticmethod
    def get_class_overview():
        """
        Class-wide statistics for the instructor dashboard.

        Returns:
        {
            "total_students":    25,
            "total_quizzes":     120,
            "class_average":     68.4,
            "at_risk_students":  [ list of at-risk student summaries ],
            "top_performers":    [ list of top student summaries ]
        }
        """
        students = UserService.get_all_students()

        if not students:
            return {
                "total_students":   0,
                "total_quizzes":    0,
                "class_average":    0.0,
                "at_risk_students": [],
                "top_performers":   []
            }

        total_quizzes = (
            QuizAttempt.query
            .filter(QuizAttempt.completed_at.isnot(None))
            .count()
        )

        class_avg_result = (
            db.session.query(func.avg(QuizAttempt.score))
            .filter(QuizAttempt.completed_at.isnot(None))
            .scalar()
        )
        class_average = round(float(class_avg_result), 1) if class_avg_result else 0.0

        at_risk = []
        top_performers = []

        for student in students:
            summary = UserService.get_student_summary(student.id)
            if not summary:
                continue
            if summary["is_at_risk"]:
                at_risk.append(summary)
            if summary["total_quizzes"] >= 2 and summary["average_score"] >= 80.0:
                top_performers.append(summary)

        at_risk.sort(key=lambda s: s["average_score"])
        top_performers.sort(key=lambda s: s["average_score"], reverse=True)

        return {
            "total_students":   len(students),
            "total_quizzes":    total_quizzes,
            "class_average":    class_average,
            "at_risk_students": at_risk,
            "top_performers":   top_performers
        }


class QuizService:
    """
    Helper functions for quiz generation and performance tracking.
    The most important method is determine_difficulty() — the
    core of the adaptive learning system.
    """

    @staticmethod
    def get_all_topics():
        """
        Returns a list of all unique topic names in the question bank.
        Runs: SELECT DISTINCT topic FROM questions

        Example: ["Data Structures", "Algorithms", "Databases", ...]
        """
        results = db.session.query(Question.topic).distinct().all()
        return [row[0] for row in results]

    @staticmethod
    def get_student_topic_scores(user_id):
        """
        Returns average score per topic for one student.

        Example output:
        {
            "Data Structures": { "average_score": 75.0, "attempts": 3 },
            "Algorithms":      { "average_score": 55.0, "attempts": 2 }
        }
        """
        results = (
            db.session.query(
                QuizAttempt.topic,
                func.avg(QuizAttempt.score).label("avg_score"),
                func.count(QuizAttempt.id).label("attempt_count")
            )
            .filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.completed_at.isnot(None)
            )
            .group_by(QuizAttempt.topic)
            .all()
        )
        return {
            row.topic: {
                "average_score": round(float(row.avg_score), 1),
                "attempts":      row.attempt_count
            }
            for row in results
        }

    @staticmethod
    def get_recent_attempts(user_id, limit=10):
        """
        Returns the most recent completed quizzes for a student.
        Ordered newest first. Used for quiz history display.
        """
        return (
            QuizAttempt.query
            .filter_by(user_id=user_id)
            .filter(QuizAttempt.completed_at.isnot(None))
            .order_by(QuizAttempt.completed_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def determine_difficulty(user_id, topic):
        """
        ════════════════════════════════════════════════════
        THE ADAPTIVE QUIZ ALGORITHM
        ════════════════════════════════════════════════════
        Decides what difficulty level to give the student next.

        HOW IT WORKS:
        1. Look at student's 3 most recent quizzes in this topic
        2. Calculate their average score
        3. Apply these rules:

           No history     → 1 (Easy)   — start everyone easy
           Average < 55%  → 1 (Easy)   — student is struggling
           Average 55-79% → 2 (Medium) — making good progress
           Average >= 80% → 3 (Hard)   — excelling, push further

        We use only the 3 MOST RECENT quizzes so that improvement
        is rewarded quickly — a student who struggled months ago
        but has improved recently gets harder questions now.

        Returns: 1, 2, or 3
        ════════════════════════════════════════════════════
        """
        recent = (
            QuizAttempt.query
            .filter_by(user_id=user_id, topic=topic)
            .filter(QuizAttempt.completed_at.isnot(None))
            .order_by(QuizAttempt.completed_at.desc())
            .limit(3)
            .all()
        )

        if not recent:
            return 1   # No history → start easy

        avg = sum(a.score for a in recent) / len(recent)

        if avg >= 80:
            return 3
        elif avg >= 55:
            return 2
        else:
            return 1

    @staticmethod
    def get_score_history(user_id, limit=20):
        """
        Returns a chronological list of quiz scores.
        Used to draw the progress-over-time chart in Stage 6.

        Example output:
        [
            { "date": "2025-01-10", "score": 45.0, "topic": "Algorithms" },
            { "date": "2025-01-20", "score": 60.0, "topic": "Algorithms" },
            { "date": "2025-02-01", "score": 78.0, "topic": "Algorithms" }
        ]
        """
        attempts = (
            QuizAttempt.query
            .filter_by(user_id=user_id)
            .filter(QuizAttempt.completed_at.isnot(None))
            .order_by(QuizAttempt.completed_at.asc())   # Oldest first for chart
            .limit(limit)
            .all()
        )
        return [
            {
                "date":       a.completed_at.strftime("%Y-%m-%d"),
                "score":      a.score,
                "topic":      a.topic,
                "difficulty": a.difficulty,
                "correct_q":  a.correct_q,
                "total_q":    a.total_q
            }
            for a in attempts
        ]
