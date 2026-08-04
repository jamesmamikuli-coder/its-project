# ============================================================
#  config/settings.py  —  All configuration settings live here
#  Think of this as the "control panel" for the entire backend
# ============================================================

import os               # Used to read environment variables
from datetime import timedelta  # Used to set token expiry time


class Config:
    """
    This class holds ALL settings for our Flask app.
    Flask reads these when we call app.config.from_object(Config)
    """

    # ── Secret Key ──
    # Used by Flask to sign cookies and sessions securely.
    # IMPORTANT: Change this to something random before deploying!
    # os.environ.get(...) means: "read from environment variable,
    # and if not found, use the default value provided"
    SECRET_KEY = os.environ.get("SECRET_KEY", "its-super-secret-key-change-in-production")

    # ── Database Connection ──
    # This is the URL Flask uses to connect to PostgreSQL.
    # Format: postgresql://username:password@host:port/database_name
    #
    # DEFAULT assumes:
    #   username = postgres
    #   password = postgres
    #   host     = localhost
    #   port     = 5432  (PostgreSQL default)
    #   database = its_db
    #
    # ⚠️  IMPORTANT: Change 'postgres' password below to match
    #     the password you set when installing PostgreSQL!
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:admin123@localhost:5432/its_db"
    )

    # Disable a Flask-SQLAlchemy feature we don't need
    # (it tracks every change to objects — wastes memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── JWT (JSON Web Token) Settings ──
    # JWT tokens are like "login tickets" — the user gets one
    # after logging in, and sends it with every future request
    # so the server knows who they are.
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-change-me")

    # How long before a token expires (user must log in again)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # 24 hours

    # ── App Settings ──
    DEBUG = True    # Show detailed errors (turn OFF in production)

    # ── NLP Settings ──
    # Minimum similarity score (0.0 to 1.0) for the Q&A engine
    # to return an answer. Below this = "I don't know"
    QA_CONFIDENCE_THRESHOLD = 0.15

    # Number of top answers to retrieve before picking the best
    QA_TOP_K_RESULTS = 3
