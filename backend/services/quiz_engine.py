# ============================================================
#  services/quiz_engine.py
#  THE ADAPTIVE QUIZ ENGINE
#
#  This is the "intelligence" behind quiz generation.
#  Instead of giving every student the same questions at the
#  same difficulty, this engine adapts to each student's
#  performance — making it an actual Intelligent Tutoring System.
#
#  ── HOW ADAPTIVE LEARNING WORKS ─────────────────────────────
#
#  Every student starts at difficulty level 1 (Easy).
#  After each quiz, the engine looks at their recent scores
#  and decides what difficulty to use NEXT time:
#
#  ┌─────────────────────────────────┬────────────────────────┐
#  │ Recent Average Score            │ Next Quiz Difficulty   │
#  ├─────────────────────────────────┼────────────────────────┤
#  │ First time (no history)         │ 1 — Easy               │
#  │ Average < 50%  (struggling)     │ 1 — Easy               │
#  │ Average 50–79% (progressing)    │ 2 — Medium             │
#  │ Average ≥ 80%  (excelling)      │ 3 — Hard               │
#  └─────────────────────────────────┴────────────────────────┘
#
#  The engine looks at the student's LAST 3 quizzes (not all time)
#  so it adapts quickly to recent improvement or decline.
#
#  ── QUIZ FLOW ────────────────────────────────────────────────
#
#  1. Student calls GET /api/quiz/start?topic=Algorithms
#  2. Engine checks their recent scores → picks difficulty
#  3. Engine selects N random questions at that difficulty
#  4. A QuizAttempt record is created in the database
#  5. Questions (WITHOUT answers) are sent to the frontend
#  6. Student answers all questions, clicks Submit
#  7. Student calls POST /api/quiz/submit with their answers
#  8. Engine scores each answer, saves results, returns feedback
# ============================================================

import logging
from datetime import datetime

from sqlalchemy import func

from extensions import db
from models.models import Question, QuizAttempt, QuizAnswer

logger = logging.getLogger(__name__)

# Number of questions per quiz (can be changed here for the whole app)
QUESTIONS_PER_QUIZ = 5


class QuizEngine:
    """
    Handles all quiz logic:
      - Determining the right difficulty for a student
      - Selecting random questions from the question bank
      - Scoring submitted answers
      - Saving all results to the database
    """

    # ── DIFFICULTY SELECTION ──────────────────────────────────

    def determine_difficulty(self, user_id, topic):
        """
        Decide what difficulty level to give a student for their
        next quiz on a given topic.

        This is the ADAPTIVE part of the system. It looks at how
        the student has done in their last 3 quizzes on this topic
        and moves them up, keeps them, or moves them down.

        Parameters:
            user_id (int) : ID of the student
            topic   (str) : Topic name e.g. "Algorithms"

        Returns:
            int: 1 (Easy), 2 (Medium), or 3 (Hard)

        Example:
            difficulty = engine.determine_difficulty(user_id=5, topic="Algorithms")
            # Returns 2 if student has been scoring 60–79% recently
        """
        # Fetch the student's last 3 completed quizzes for this topic
        # We use .isnot(None) to filter only COMPLETED quizzes
        # (started but not submitted quizzes are excluded)
        recent_attempts = (
            QuizAttempt.query
            .filter_by(user_id=user_id, topic=topic)
            .filter(QuizAttempt.completed_at.isnot(None))
            .order_by(QuizAttempt.completed_at.desc())   # newest first
            .limit(3)
            .all()
        )

        # No history for this topic → start with Easy questions
        # We don't want to overwhelm a student on their first attempt
        if not recent_attempts:
            logger.info(f"User {user_id} has no history in {topic} → difficulty 1")
            return 1

        # Calculate average score across those recent attempts
        # sum([80, 70, 60]) / 3 = 70.0
        avg_score = sum(a.score for a in recent_attempts) / len(recent_attempts)

        logger.info(f"User {user_id} recent avg in {topic}: {avg_score:.1f}%")

        # Apply the adaptive rules
        if avg_score >= 80:
            return 3   # Excelling → challenge them with Hard questions
        elif avg_score >= 50:
            return 2   # Progressing → Medium questions
        else:
            return 1   # Struggling → keep it Easy to build confidence

    def get_difficulty_label(self, difficulty):
        """
        Convert a difficulty number to a human-readable label.

        Returns:
            "Easy"   for 1
            "Medium" for 2
            "Hard"   for 3
        """
        return {1: "Easy", 2: "Medium", 3: "Hard"}.get(difficulty, "Easy")

    # ── QUESTION SELECTION ────────────────────────────────────

    def get_questions(self, topic, difficulty, count=QUESTIONS_PER_QUIZ):
        """
        Fetch a random set of questions for a quiz.

        The questions are RANDOMISED on every call using
        PostgreSQL's RANDOM() function, so a student gets
        different questions each time they take a quiz.

        Parameters:
            topic      (str) : e.g. "Data Structures"
            difficulty (int) : 1=Easy, 2=Medium, 3=Hard
            count      (int) : how many questions to return

        Returns:
            list of Question objects

        If there aren't enough questions at the requested
        difficulty, we fall back to any difficulty for that topic
        to ensure the quiz always has questions.
        """
        # Primary attempt: get questions at the exact difficulty
        questions = (
            Question.query
            # ilike = case-insensitive match
            # "%Data Structures%" matches "data structures", "Data Structures", etc.
            .filter(Question.topic.ilike(f"%{topic}%"))
            .filter_by(difficulty=difficulty)
            .order_by(func.random())   # RANDOM() shuffles results each time
            .limit(count)
            .all()
        )

        # Fallback: not enough questions at this difficulty?
        # Get any questions from this topic regardless of difficulty
        if len(questions) < count:
            logger.warning(
                f"Not enough questions for topic={topic} difficulty={difficulty}. "
                f"Falling back to any difficulty."
            )
            questions = (
                Question.query
                .filter(Question.topic.ilike(f"%{topic}%"))
                .order_by(func.random())
                .limit(count)
                .all()
            )

        return questions

    def get_available_topics(self):
        """
        Return a list of all unique topics in the question bank.

        Used by the frontend to populate the topic dropdown
        on the quiz start page.

        Returns:
            list of strings e.g.:
            ["Algorithms", "Data Structures", "Databases",
             "Programming Concepts"]
        """
        # SELECT DISTINCT topic FROM questions ORDER BY topic
        results = (
            db.session.query(Question.topic)
            .distinct()
            .order_by(Question.topic)
            .all()
        )
        # Each result is a tuple: ("Algorithms",)
        # We take index [0] to get just the string
        return [row[0] for row in results]

    # ── QUIZ CREATION ─────────────────────────────────────────

    def start_quiz(self, user_id, topic):
        """
        Create a new quiz session for a student.

        Steps:
          1. Determine the appropriate difficulty for this student
          2. Select random questions at that difficulty
          3. Create a QuizAttempt record in the database
          4. Return the questions (WITHOUT correct answers)

        Parameters:
            user_id (int) : the student's ID
            topic   (str) : which topic they want to be quizzed on

        Returns a dict:
        {
            "attempt_id": 7,
            "topic":      "Algorithms",
            "difficulty": 2,
            "difficulty_label": "Medium",
            "questions":  [ {question dict without answer}, ... ],
            "total_questions": 5
        }

        Returns None if no questions exist for this topic.
        """
        # Step 1: Choose difficulty based on student's history
        difficulty = self.determine_difficulty(user_id, topic)
        difficulty_label = self.get_difficulty_label(difficulty)

        # Step 2: Select random questions
        questions = self.get_questions(topic, difficulty)

        if not questions:
            logger.error(f"No questions found for topic: {topic}")
            return None

        # Step 3: Save the quiz attempt to the database
        # We create it NOW (before the student answers) so we can
        # track when they started and how long they took
        attempt = QuizAttempt(
            user_id    = user_id,
            topic      = topic,
            difficulty = difficulty,
            # started_at is set automatically by the model default
        )
        db.session.add(attempt)
        db.session.commit()

        logger.info(
            f"Quiz started: user={user_id} topic={topic} "
            f"difficulty={difficulty} attempt_id={attempt.id}"
        )

        # Step 4: Return quiz data to the frontend
        # IMPORTANT: to_dict(include_answer=False) hides the correct answer
        # The student must not see the answer during the quiz!
        return {
            "attempt_id":      attempt.id,
            "topic":           topic,
            "difficulty":      difficulty,
            "difficulty_label": difficulty_label,
            "questions":       [q.to_dict(include_answer=False) for q in questions],
            "total_questions": len(questions),
        }

    # ── QUIZ SCORING ──────────────────────────────────────────

    def submit_quiz(self, attempt_id, user_id, answers_data):
        """
        Score a submitted quiz and save all results to the database.

        Parameters:
            attempt_id   (int)  : the QuizAttempt ID from start_quiz()
            user_id      (int)  : who is submitting (security check)
            answers_data (list) : list of answer dicts from frontend:
                [
                    {
                        "question_id":     3,
                        "selected_answer": "B",
                        "time_taken_secs": 15
                    },
                    ...
                ]

        Returns a dict with full results, or None if attempt not found.

        HOW SCORING WORKS:
          - For each submitted answer, look up the correct answer
            from the database (students can't fake it)
          - Count how many match
          - score = (correct / total) * 100
          - Save a QuizAnswer row for each question
          - Update the QuizAttempt with the final score
        """
        # Find the QuizAttempt — verify it belongs to this user
        # This prevents one student from submitting answers for another
        attempt = QuizAttempt.query.filter_by(
            id      = attempt_id,
            user_id = user_id
        ).first()

        if not attempt:
            logger.warning(f"Attempt {attempt_id} not found for user {user_id}")
            return None

        # Don't allow submitting twice
        if attempt.completed_at is not None:
            logger.warning(f"Attempt {attempt_id} already submitted")
            return None

        correct_count = 0
        answer_results = []

        # Score each answer
        for ans in answers_data:
            question_id     = ans.get("question_id")
            selected_answer = ans.get("selected_answer", "").upper().strip()
            time_taken_secs = ans.get("time_taken_secs", 0)

            # Look up the question to get the correct answer
            question = Question.query.get(question_id)
            if not question:
                continue   # Skip if question ID is invalid

            # Compare the student's answer to the correct one
            is_correct = (selected_answer == question.correct_answer.upper())
            if is_correct:
                correct_count += 1

            # Save this individual answer to the database
            quiz_answer = QuizAnswer(
                attempt_id      = attempt_id,
                question_id     = question_id,
                selected_answer = selected_answer,
                is_correct      = is_correct,
                time_taken_secs = time_taken_secs,
            )
            db.session.add(quiz_answer)

            # Collect result details for the response
            answer_results.append({
                "question_id":     question_id,
                "question_text":   question.question_text,
                "selected_answer": selected_answer,
                "correct_answer":  question.correct_answer,
                "is_correct":      is_correct,
                "explanation":     question.explanation,
                "topic":           question.topic,
                "time_taken_secs": time_taken_secs,
            })

        # Calculate overall score as a percentage
        total = len(answers_data)
        score = round((correct_count / total * 100), 1) if total > 0 else 0.0

        # Update the QuizAttempt record with final results
        attempt.score        = score
        attempt.total_q      = total
        attempt.correct_q    = correct_count
        attempt.completed_at = datetime.utcnow()   # Mark as completed

        db.session.commit()

        logger.info(
            f"Quiz submitted: attempt={attempt_id} user={user_id} "
            f"score={score}% ({correct_count}/{total})"
        )

        # Build a performance message for the student
        feedback_message = self._get_feedback_message(score)

        # Determine what difficulty to recommend next
        next_difficulty = self.determine_difficulty(user_id, attempt.topic)
        next_label      = self.get_difficulty_label(next_difficulty)

        return {
            "attempt_id":      attempt_id,
            "score":           score,
            "correct_q":       correct_count,
            "total_q":         total,
            "topic":           attempt.topic,
            "difficulty":      attempt.difficulty,
            "difficulty_label": self.get_difficulty_label(attempt.difficulty),
            "feedback_message": feedback_message,
            "next_difficulty":  next_difficulty,
            "next_difficulty_label": next_label,
            "answers":         answer_results,
            "duration_seconds": attempt.duration_seconds,
        }

    def _get_feedback_message(self, score):
        """
        Return an encouraging message based on the student's score.

        This is displayed on the results page after submitting a quiz.
        """
        if score == 100:
            return "🏆 Perfect score! Outstanding work!"
        elif score >= 80:
            return "🌟 Excellent! You have a strong grasp of this topic."
        elif score >= 60:
            return "👍 Good effort! Review the incorrect answers to improve further."
        elif score >= 40:
            return "📚 Keep studying! Focus on the topics you got wrong."
        else:
            return "💪 Don't give up! Review the material and try again — you can do it."

    # ── HISTORY & STATS ───────────────────────────────────────

    def get_quiz_history(self, user_id, limit=20):
        """
        Get a student's completed quiz history, newest first.

        Parameters:
            user_id (int) : the student's ID
            limit   (int) : max number of records to return

        Returns:
            list of QuizAttempt objects
        """
        return (
            QuizAttempt.query
            .filter_by(user_id=user_id)
            .filter(QuizAttempt.completed_at.isnot(None))
            .order_by(QuizAttempt.completed_at.desc())
            .limit(limit)
            .all()
        )

    def get_attempt_detail(self, attempt_id, user_id):
        """
        Get full details of one specific quiz attempt including
        all individual answers and correct answers.

        Used on the quiz results review page.

        Parameters:
            attempt_id (int) : which quiz attempt
            user_id    (int) : security check — must be the owner

        Returns:
            dict with attempt info and all answers, or None if not found
        """
        attempt = QuizAttempt.query.filter_by(
            id=attempt_id, user_id=user_id
        ).first()

        if not attempt or not attempt.completed_at:
            return None

        return {
            **attempt.to_dict(),
            "answers": [a.to_dict() for a in attempt.answers],
            "difficulty_label": self.get_difficulty_label(attempt.difficulty),
        }


# ── Global engine instance ────────────────────────────────────
# One instance shared across all requests — no need to
# re-create it on every API call
quiz_engine = QuizEngine()
