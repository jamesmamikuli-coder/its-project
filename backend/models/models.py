# ============================================================
#  models/models.py
#  DATABASE TABLE DEFINITIONS
#
#  This file defines all the tables in our PostgreSQL database.
#  Each Python CLASS here = one TABLE in the database.
#  Each CLASS ATTRIBUTE = one COLUMN in that table.
#
#  SQLAlchemy reads these class definitions and automatically
#  creates the real tables when we call db.create_all() in app.py
#
#  TABLES IN THIS FILE:
#  ┌─────────────────────┬────────────────────────────────────────┐
#  │ Class Name          │ What it stores                         │
#  ├─────────────────────┼────────────────────────────────────────┤
#  │ User                │ All accounts (students + instructors)  │
#  │ Question            │ Quiz questions bank                    │
#  │ QuizAttempt         │ One quiz session per student           │
#  │ QuizAnswer          │ Each individual answer inside a quiz   │
#  │ KnowledgeArticle    │ CS articles for the Q&A chatbot        │
#  │ QALog               │ Logs every chatbot question asked      │
#  └─────────────────────┴────────────────────────────────────────┘
# ============================================================

from datetime import datetime

# We import 'db' from app.py — this is the SQLAlchemy object
# that connects Python to PostgreSQL
from extensions import db


# ============================================================
#  TABLE 1: users
#  Stores every registered account on the platform
# ============================================================
class User(db.Model):

    # __tablename__ tells SQLAlchemy what to name the table in PostgreSQL
    # Without this it would use the class name lowercased ("user")
    __tablename__ = "users"

    # ── Columns ──────────────────────────────────────────────
    # primary_key=True  → this column is the unique ID for each row
    # db.Integer        → stores whole numbers (1, 2, 3, ...)
    id = db.Column(db.Integer, primary_key=True)

    # db.String(100)  → stores text up to 100 characters
    # nullable=False  → this column MUST have a value (can't be empty)
    name = db.Column(db.String(100), nullable=False)

    # unique=True → no two users can have the same email
    email = db.Column(db.String(120), unique=True, nullable=False)

    # We store the HASHED password, never the plain text one
    # Hashed passwords are long strings like: pbkdf2:sha256:260000$abc...
    # That's why we need 256 characters
    password = db.Column(db.String(256), nullable=False)

    # Either "student" or "instructor"
    # default="student" → if role isn't specified, it becomes "student"
    role = db.Column(db.String(20), default="student")

    # db.DateTime        → stores date and time
    # default=datetime.utcnow → automatically set to current time when created
    # Note: utcnow is a function reference (no brackets) — SQLAlchemy calls
    # it at insert time, not when Python reads this class definition
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ── Relationships ─────────────────────────────────────────
    # This tells SQLAlchemy: "A User can have MANY QuizAttempts"
    # It creates a convenient shortcut: user.quiz_attempts gives us
    # a list of all that user's quiz attempts
    #
    # backref="user" → on a QuizAttempt object, attempt.user gives the User
    # lazy=True      → don't load quiz_attempts from DB until we ask for it
    # cascade="all, delete-orphan" → if we delete a user, automatically
    #   delete all their quiz_attempts and qa_logs too (no orphan records)
    quiz_attempts = db.relationship(
        "QuizAttempt",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    qa_logs = db.relationship(
        "QALog",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # ── Methods ───────────────────────────────────────────────

    def to_dict(self):
        """
        Convert this User object into a plain Python dictionary.
        We use this when we want to send user data back to the
        frontend as JSON.

        IMPORTANT: We deliberately leave out 'password' here.
        We should NEVER send password hashes to the frontend!
        """
        return {
            "id":         self.id,
            "name":       self.name,
            "email":      self.email,
            "role":       self.role,
            # .isoformat() converts datetime to a string like "2024-01-15T10:30:00"
            # JSON can't store datetime objects directly, only strings
            "created_at": self.created_at.isoformat()
        }

    def get_average_score(self):
        """
        Calculate this student's average quiz score as a percentage.
        Returns 0.0 if they haven't completed any quizzes yet.

        Example: if they scored 70%, 80%, 60% → returns 70.0
        """
        # Get only the completed quiz attempts (not abandoned ones)
        # A quiz is "completed" when completed_at has a date/time value
        completed = [a for a in self.quiz_attempts if a.completed_at is not None]

        if not completed:
            return 0.0  # No completed quizzes yet

        # sum() adds up all scores, len() counts how many there are
        return round(sum(a.score for a in completed) / len(completed), 1)

    def get_total_quizzes(self):
        """
        Count how many quizzes this student has fully completed.
        """
        return sum(1 for a in self.quiz_attempts if a.completed_at is not None)

    def __repr__(self):
        """
        This is what Python shows when you print a User object.
        Example: <User 3: Amina (student)>
        Useful for debugging.
        """
        return f"<User {self.id}: {self.name} ({self.role})>"


# ============================================================
#  TABLE 2: questions
#  The quiz question bank — all multiple choice questions
# ============================================================
class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)

    # The subject area, e.g. "Data Structures", "Algorithms"
    topic = db.Column(db.String(100), nullable=False)

    # More specific area, e.g. "Linked Lists", "Binary Search"
    # nullable=True (no nullable=False) means this can be empty
    subtopic = db.Column(db.String(100))

    # db.Text → stores long strings (no character limit)
    # Used for the actual question sentence
    question_text = db.Column(db.Text, nullable=False)

    # The four answer choices for the multiple choice question
    option_a = db.Column(db.String(300), nullable=False)
    option_b = db.Column(db.String(300), nullable=False)
    option_c = db.Column(db.String(300), nullable=False)
    option_d = db.Column(db.String(300), nullable=False)

    # Which option is correct — stores just one letter: 'A', 'B', 'C', or 'D'
    correct_answer = db.Column(db.String(1), nullable=False)

    # The explanation shown AFTER the student answers
    explanation = db.Column(db.Text)

    # How hard the question is:
    # 1 = Easy (beginner)
    # 2 = Medium (intermediate)
    # 3 = Hard (advanced)
    difficulty = db.Column(db.Integer, default=1)

    def to_dict(self, include_answer=False):
        """
        Convert this Question to a dictionary for sending as JSON.

        include_answer=False (default):
            Used DURING a quiz — we send the question without
            revealing the correct answer to the student!

        include_answer=True:
            Used on the RESULTS page — we now show which answer
            was correct and explain why.
        """
        data = {
            "id":            self.id,
            "topic":         self.topic,
            "subtopic":      self.subtopic,
            "question_text": self.question_text,
            "option_a":      self.option_a,
            "option_b":      self.option_b,
            "option_c":      self.option_c,
            "option_d":      self.option_d,
            "difficulty":    self.difficulty,
        }
        # Only add the answer if the caller specifically asked for it
        if include_answer:
            data["correct_answer"] = self.correct_answer
            data["explanation"]    = self.explanation

        return data

    def __repr__(self):
        return f"<Question {self.id}: [{self.topic}] {self.question_text[:40]}...>"


# ============================================================
#  TABLE 3: quiz_attempts
#  One row is created every time a student STARTS a quiz.
#  It gets updated with the score when they SUBMIT it.
# ============================================================
class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"

    id = db.Column(db.Integer, primary_key=True)

    # db.ForeignKey("users.id") → links this row to a row in the users table
    # This is how we know WHICH student took this quiz
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Which topic this quiz covered, e.g. "Data Structures"
    topic = db.Column(db.String(100))

    # Score as a percentage: 0.0 to 100.0
    # e.g. 75.0 means the student got 75% correct
    score = db.Column(db.Float, default=0.0)

    # How many questions were in this quiz
    total_q = db.Column(db.Integer, default=0)

    # How many the student got right
    correct_q = db.Column(db.Integer, default=0)

    # The difficulty level used: 1=Easy, 2=Medium, 3=Hard
    difficulty = db.Column(db.Integer, default=1)

    # When the student clicked "Start Quiz"
    started_at = db.Column(db.DateTime, default=datetime.utcnow)

    # When the student clicked "Submit Quiz"
    # nullable=True (default) means it starts as NULL/None
    # We only fill this in when they actually submit
    completed_at = db.Column(db.DateTime, nullable=True)

    # One QuizAttempt has many QuizAnswers (one per question)
    answers = db.relationship(
        "QuizAnswer",
        backref="attempt",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def is_completed(self):
        """
        @property means we can call this like: attempt.is_completed
        instead of: attempt.is_completed()
        Returns True if the student submitted this quiz.
        """
        return self.completed_at is not None

    @property
    def duration_seconds(self):
        """
        How long the student took to complete the quiz, in seconds.
        Returns None if the quiz isn't finished yet.
        """
        if self.completed_at and self.started_at:
            # timedelta is the difference between two datetime objects
            # .total_seconds() converts it to a plain number
            return int((self.completed_at - self.started_at).total_seconds())
        return None

    def to_dict(self):
        return {
            "id":               self.id,
            "user_id":          self.user_id,
            "topic":            self.topic,
            "score":            self.score,
            "total_q":          self.total_q,
            "correct_q":        self.correct_q,
            "difficulty":       self.difficulty,
            "is_completed":     self.is_completed,
            "duration_seconds": self.duration_seconds,
            "started_at":       self.started_at.isoformat(),
            "completed_at":     self.completed_at.isoformat() if self.completed_at else None,
        }

    def __repr__(self):
        return f"<QuizAttempt {self.id}: user={self.user_id} score={self.score}%>"


# ============================================================
#  TABLE 4: quiz_answers
#  One row per question answered within a quiz.
#  If a quiz has 5 questions, there will be 5 QuizAnswer rows
#  all linked to the same QuizAttempt.
# ============================================================
class QuizAnswer(db.Model):
    __tablename__ = "quiz_answers"

    id = db.Column(db.Integer, primary_key=True)

    # Which quiz session this answer belongs to
    attempt_id = db.Column(db.Integer, db.ForeignKey("quiz_attempts.id"), nullable=False)

    # Which question was being answered
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)

    # What the student chose: 'A', 'B', 'C', or 'D'
    selected_answer = db.Column(db.String(1))

    # Did they get it right? True or False
    is_correct = db.Column(db.Boolean, default=False)

    # How many seconds it took to answer this specific question
    time_taken_secs = db.Column(db.Integer)

    # This gives us direct access to the Question object
    # e.g. answer.question.question_text gives us the question text
    question = db.relationship("Question")

    def to_dict(self):
        """
        Full details including the correct answer.
        We use this on the results page AFTER the quiz is submitted.
        """
        return {
            "question_id":     self.question_id,
            "question_text":   self.question.question_text,
            "selected_answer": self.selected_answer,
            "is_correct":      self.is_correct,
            "correct_answer":  self.question.correct_answer,
            "explanation":     self.question.explanation,
            "time_taken_secs": self.time_taken_secs,
            "topic":           self.question.topic,
            "difficulty":      self.question.difficulty,
        }


# ============================================================
#  TABLE 5: knowledge_articles
#  The knowledge base that the Q&A chatbot searches through.
#  Each article is about one CS concept (e.g. "What is a Stack?")
# ============================================================
class KnowledgeArticle(db.Model):
    __tablename__ = "knowledge_articles"

    id = db.Column(db.Integer, primary_key=True)

    # Subject area, e.g. "Data Structures"
    topic = db.Column(db.String(100), nullable=False)

    # Short title, e.g. "What is a Stack?"
    title = db.Column(db.String(200), nullable=False)

    # The full explanation — can be multiple paragraphs
    content = db.Column(db.Text, nullable=False)

    # Comma-separated keywords to help matching
    # e.g. "stack, LIFO, push, pop, call stack"
    keywords = db.Column(db.Text)

    def to_dict(self):
        return {
            "id":       self.id,
            "topic":    self.topic,
            "title":    self.title,
            "content":  self.content,
            "keywords": self.keywords,
        }

    def __repr__(self):
        return f"<KnowledgeArticle {self.id}: {self.title}>"


# ============================================================
#  TABLE 6: qa_logs
#  Records every question a student asks the chatbot.
#  This powers the analytics dashboard (Stage 5).
#  Instructors can see what topics students are confused about.
# ============================================================
class QALog(db.Model):
    __tablename__ = "qa_logs"

    id = db.Column(db.Integer, primary_key=True)

    # Who asked the question
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # The exact text the student typed into the chatbot
    question = db.Column(db.Text, nullable=False)

    # What the chatbot replied with
    answer = db.Column(db.Text)

    # Which topic the system matched this question to
    # e.g. "Data Structures" or "Algorithms"
    matched_topic = db.Column(db.String(100))

    # How confident the NLP engine was: 0.0 (no match) to 1.0 (perfect match)
    # Values below 0.15 mean "I don't know the answer"
    confidence = db.Column(db.Float, default=0.0)

    # Optional: did the student find this answer helpful?
    # True = thumbs up, False = thumbs down, None = no feedback given
    was_helpful = db.Column(db.Boolean, nullable=True)

    # Automatically records when the question was asked
    asked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":            self.id,
            "user_id":       self.user_id,
            "question":      self.question,
            "answer":        self.answer,
            "matched_topic": self.matched_topic,
            "confidence":    self.confidence,
            "was_helpful":   self.was_helpful,
            "asked_at":      self.asked_at.isoformat(),
        }

    def __repr__(self):
        return f"<QALog {self.id}: '{self.question[:40]}'>"
