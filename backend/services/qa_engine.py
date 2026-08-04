# ============================================================
#  services/qa_engine.py
#  THE NLP QUESTION ANSWERING ENGINE
#
#  This is the "brain" of the chatbot. When a student types a
#  question like "What is a linked list?", this file:
#
#    1. Loads all knowledge articles from the database
#    2. Converts every article + the student question into
#       numbers using TF-IDF (explained below)
#    3. Measures how similar the question is to each article
#    4. Returns the most similar article as the answer
#
#  ── WHAT IS TF-IDF? ──────────────────────────────────────
#
#  TF-IDF stands for Term Frequency-Inverse Document Frequency.
#  It is a way to convert text into numbers so a computer can
#  measure how "similar" two pieces of text are.
#
#  TF  (Term Frequency)        = how often a word appears in one document
#  IDF (Inverse Doc Frequency) = how rare a word is across ALL documents
#
#  Words that appear in many documents (like "the", "is", "a")
#  get a LOW score — they don't help identify the topic.
#
#  Words that appear in few documents (like "recursion", "heap")
#  get a HIGH score — they strongly identify the topic.
#
#  Example:
#    Student asks: "how does binary search work?"
#    Article 1 (Binary Search): TF-IDF score = 0.87  ← BEST MATCH
#    Article 2 (Bubble Sort):   TF-IDF score = 0.12
#    Article 3 (Linked Lists):  TF-IDF score = 0.03
#
#  We return Article 1 as the answer.
#
#  ── WHAT IS COSINE SIMILARITY? ───────────────────────────
#
#  After TF-IDF converts text to numbers (vectors), we measure
#  similarity using "cosine similarity".
#
#  Imagine each document as an arrow pointing in space.
#  Cosine similarity measures the ANGLE between two arrows:
#    - Angle = 0°  → arrows point the same way → similarity = 1.0 (identical)
#    - Angle = 90° → arrows are perpendicular → similarity = 0.0 (nothing in common)
#
#  We use this to rank which article best answers the question.
#
#  ── FILES USED BY THIS ENGINE ────────────────────────────
#
#  Knowledge articles come from the 'knowledge_articles' table
#  in PostgreSQL (loaded by seed_data.py).
#
#  The engine is "re-fitted" (retrained) each time the Flask
#  server starts, using whatever articles are in the database.
# ============================================================

import re
import logging

import numpy as np

# TfidfVectorizer: converts text into TF-IDF number vectors
from sklearn.feature_extraction.text import TfidfVectorizer

# cosine_similarity: measures how similar two vectors are (0.0 to 1.0)
from sklearn.metrics.pairwise import cosine_similarity

# Set up logging so we can see debug messages in the terminal
logger = logging.getLogger(__name__)


class QAEngine:
    """
    The Question Answering Engine.

    This class:
    1. Loads knowledge articles from the database
    2. Builds a TF-IDF model from them
    3. Answers student questions by finding the most similar article

    USAGE EXAMPLE:
        engine = QAEngine()
        engine.fit(articles)   # train on knowledge base
        result = engine.answer("What is a stack?")
        print(result["answer"])
    """

    def __init__(self):
        """
        Set up the engine with default settings.
        We don't load data here — that happens in fit().
        """

        # The TF-IDF vectorizer — converts text to number vectors.
        # Settings explained:
        #   stop_words="english" → ignore common words like "the", "is", "a"
        #                         These words appear everywhere and don't help matching
        #   ngram_range=(1, 2)   → consider single words AND pairs of words
        #                         e.g. "binary search" is treated as ONE feature
        #                         not just "binary" and "search" separately
        #   max_features=5000    → only keep the 5000 most important words
        #                         (limits memory usage)
        #   min_df=1             → include a word even if it only appears once
        #                         (important for a small knowledge base)
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
            min_df=1,
        )

        # These are set when fit() is called:
        self.article_vectors = None   # TF-IDF matrix of all articles
        self.articles        = []     # List of KnowledgeArticle objects
        self.is_fitted       = False  # Has the engine been trained yet?

        # Minimum confidence score to return an answer.
        # Below this value, we say "I don't know" instead of guessing.
        # Range: 0.0 (no match) to 1.0 (perfect match)
        self.confidence_threshold = 0.12

    def _build_document(self, article):
        """
        Combine an article's title, keywords, and content into
        one single string for TF-IDF processing.

        We weight title and keywords more heavily by repeating them.
        This makes the engine match topic names more reliably.

        Example input article:
            title    = "What is a Stack?"
            keywords = "stack, LIFO, push, pop"
            content  = "A stack is a data structure..."

        Example output:
            "What is a Stack? What is a Stack? stack LIFO push pop
             stack LIFO push pop stack LIFO push pop A stack is a..."
        """
        parts = []

        # Add title TWICE → extra weight
        if article.title:
            parts.append(article.title)
            parts.append(article.title)

        # Add keywords THREE TIMES → even more weight
        # Keywords are the most precise signal for topic matching
        if article.keywords:
            # Convert "stack, LIFO, push, pop" to "stack LIFO push pop"
            # (remove commas so each word is treated separately)
            clean_keywords = article.keywords.replace(",", " ")
            for _ in range(3):
                parts.append(clean_keywords)

        # Add the full article content once
        if article.content:
            parts.append(article.content)

        return " ".join(parts)

    def _clean_text(self, text):
        """
        Clean and normalise text before processing.

        Steps:
          1. Lowercase everything (so "Stack" and "stack" match)
          2. Remove punctuation like ?, !, :, etc.
          3. Collapse multiple spaces into one
        """
        if not text:
            return ""
        # Convert to lowercase
        text = text.lower()
        # Remove anything that is NOT a letter, number, or space
        # re.sub replaces matching characters with ""
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        # Replace multiple consecutive spaces with a single space
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def fit(self, articles):
        """
        Train the TF-IDF model using the knowledge base articles.

        This must be called once before answer() will work.
        It is called automatically when the Flask app starts.

        Parameters:
            articles: list of KnowledgeArticle objects from the database

        What happens:
            1. Build one text document per article (title + keywords + content)
            2. Feed all documents into the TF-IDF vectorizer
            3. The vectorizer learns which words are important
            4. It converts every document into a numeric vector
            5. We store these vectors to compare against future questions
        """
        if not articles:
            logger.warning("QAEngine.fit() called with no articles — engine will not work.")
            return

        self.articles = articles

        # Build a cleaned text document for each article
        documents = [
            self._clean_document(article) for article in articles
        ]

        # fit_transform() does two things at once:
        #   fit()       = learn the vocabulary and IDF weights from all documents
        #   transform() = convert each document into a TF-IDF vector
        # Result: a matrix where each ROW is an article, each COLUMN is a word
        self.article_vectors = self.vectorizer.fit_transform(documents)

        self.is_fitted = True
        logger.info(f"QAEngine fitted on {len(articles)} articles.")

    def _clean_document(self, article):
        """Build and clean a document from an article."""
        return self._clean_text(self._build_document(article))

    def answer(self, question_text):
        """
        Find the best answer to a student's question.

        Parameters:
            question_text (str): The question typed by the student
                                 e.g. "What is a linked list?"

        Returns a dictionary:
        {
            "answer":     "A linked list is...",   ← the answer text
            "title":      "What is a Linked List?",
            "topic":      "Data Structures",
            "confidence": 0.73,                    ← match score 0.0-1.0
            "found":      True                     ← False if no good match
        }

        If no article scores above confidence_threshold:
        {
            "answer":     "I'm sorry, I don't have information on that...",
            "found":      False,
            "confidence": 0.0
        }
        """
        # Safety check — engine must be fitted first
        if not self.is_fitted or self.article_vectors is None:
            return self._no_answer("The Q&A engine has not been initialised yet.")

        if not question_text or not question_text.strip():
            return self._no_answer("Please type a question.")

        # ── Step 1: Clean the student's question ─────────────
        cleaned_question = self._clean_text(question_text.strip())

        if not cleaned_question:
            return self._no_answer("Your question appears to be empty after cleaning.")

        # ── Step 2: Convert the question to a TF-IDF vector ──
        # transform() converts the question using the SAME vocabulary
        # the vectorizer learned during fit() — this is crucial.
        # If we use a different vocabulary, the comparison won't work.
        try:
            question_vector = self.vectorizer.transform([cleaned_question])
        except Exception as e:
            logger.error(f"Failed to vectorize question: {e}")
            return self._no_answer("Could not process your question.")

        # ── Step 3: Compare question to every article ─────────
        # cosine_similarity returns a 2D array like [[0.1, 0.73, 0.04, ...]]
        # We take [0] to get the flat list: [0.1, 0.73, 0.04, ...]
        # Each number is how similar the question is to that article
        similarities = cosine_similarity(question_vector, self.article_vectors)[0]

        # ── Step 4: Find the highest-scoring article ──────────
        # np.argmax() returns the INDEX of the highest value
        best_index = int(np.argmax(similarities))
        best_score = float(similarities[best_index])

        # ── Step 5: Check if the score is good enough ─────────
        if best_score < self.confidence_threshold:
            return self._no_answer(
                f"I couldn't find a good answer to that question. "
                f"Try rephrasing, or ask about: Data Structures, Algorithms, "
                f"Databases, or Programming Concepts."
            )

        # ── Step 6: Return the best matching article ──────────
        best_article = self.articles[best_index]

        return {
            "found":      True,
            "answer":     best_article.content,
            "title":      best_article.title,
            "topic":      best_article.topic,
            "confidence": round(best_score, 4),
        }

    def _no_answer(self, message):
        """
        Helper — returns a consistent "no answer found" response.
        """
        return {
            "found":      False,
            "answer":     message,
            "title":      None,
            "topic":      None,
            "confidence": 0.0,
        }

    def get_suggestions(self, topic=None):
        """
        Return a list of sample questions the student can ask.

        If topic is provided, return questions specific to that topic.
        Otherwise return a general mix.

        Used by the frontend to show "You can ask me..." prompts.
        """
        suggestions = {
            "Data Structures": [
                "What is a linked list?",
                "How does a stack work?",
                "What is a queue?",
                "What is the difference between a stack and a queue?",
                "What is a binary search tree?",
                "What is a hash table?",
            ],
            "Algorithms": [
                "What is Big O notation?",
                "How does binary search work?",
                "What is the difference between BFS and DFS?",
                "How does merge sort work?",
                "What is recursion?",
            ],
            "Databases": [
                "What is SQL?",
                "What is database normalisation?",
                "What is a foreign key?",
                "What is the difference between a primary key and foreign key?",
            ],
            "Programming Concepts": [
                "What are the 4 pillars of OOP?",
                "What is encapsulation?",
                "What is polymorphism?",
                "What is recursion and when should I use it?",
            ],
        }

        if topic and topic in suggestions:
            return suggestions[topic]

        # Return two from each topic as a general mix
        mixed = []
        for topic_questions in suggestions.values():
            mixed.extend(topic_questions[:2])
        return mixed


# ============================================================
#  GLOBAL ENGINE INSTANCE
#
#  We create ONE engine object that lives for the entire lifetime
#  of the Flask server. This avoids re-training the model on
#  every single request (which would be very slow).
#
#  The engine is initialised (fitted) once in qa_routes.py
#  when the Flask app starts.
# ============================================================
qa_engine = QAEngine()
