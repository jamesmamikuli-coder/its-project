from flask import Flask, request
from flask_cors import CORS
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from chatbot.chatbot_service import get_chatbot_response
from chatbot.memory import get_last_conversation
import psycopg2
import bcrypt
import os
# ==================================================
# APP SETUP
# ==================================================
app = Flask(__name__)
CORS(app)

# ==================================================
# DATABASE CONNECTION
# ==================================================
import os
import psycopg2

def get_db_connection():
    ssl_mode = "require" if os.getenv("DB_HOST") else "disable"

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "its_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "admin123"),
        port=os.getenv("DB_PORT", "5432"),
        sslmode=ssl_mode
    )

# ==================================================
# INITIALIZE DATABASE TABLES
# ==================================================
def init_db():

    conn = get_db_connection()
    cur = conn.cursor()

    # CHAT HISTORY TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id SERIAL PRIMARY KEY,
            user_message TEXT,
            bot_reply TEXT
        )
    """)

    # KNOWLEDGE BASE TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title TEXT,
            content TEXT
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


init_db()


# ==================================================
# HOME ROUTE
# ==================================================
@app.route("/")
def home():
    return "Backend is running ✅"


# ==================================================
# TEST ROUTE
# ==================================================
@app.route("/api/test")
def test():
    return {
        "message": "Flask API connected successfully ✅"
    }
# ==================================================
# REGISTER API
# ==================================================
@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        # HASH PASSWORD
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # SAVE USER
        cur.execute("""
            INSERT INTO users (
        name,
        username,
        email,
        password,
        role,
        created_at
    )
    VALUES (%s, %s, %s, %s, %s, NOW())
""", (
    username,
    username,
    email,
    hashed_password,
    "student"
))

        conn.commit()

        return {
            "message": "Registration successful ✅"
        }

    except Exception as e:

        print("Register Error:", e)

        return {
            "message": "Registration failed ❌"
        }

    finally:
        cur.close()
        conn.close()
        # ==================================================
# RESET PASSWORD API
# ==================================================
@app.route("/api/reset-password", methods=["POST"])
def reset_password():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        # ==========================================
        # CHECK IF EMAIL EXISTS
        # ==========================================
        cur.execute("""
            SELECT id
            FROM users
            WHERE email = %s
        """, (email,))

        user = cur.fetchone()

        if not user:

            return {
                "message": "Email not found ❌"
            }, 404

        # ==========================================
        # HASH NEW PASSWORD
        # ==========================================
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # ==========================================
        # UPDATE PASSWORD
        # ==========================================
        cur.execute("""
            UPDATE users
            SET password = %s
            WHERE email = %s
        """, (hashed_password, email))

        conn.commit()

        return {
            "message": "Password updated successfully ✅"
        }

    except Exception as e:

        print("Reset Password Error:", e)

        return {
            "message": "Password reset failed ❌"
        }, 500

    finally:

        cur.close()
        conn.close()
 # ==================================================
# LOGIN API
# ==================================================
@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        # ==========================================
        # FIND USER BY EMAIL
        # ==========================================
        cur.execute("""
            SELECT id, username, email, password, role
            FROM users
            WHERE email = %s
        """, (email,))

        user = cur.fetchone()

        # ==========================================
        # USER EXISTS
        # ==========================================
        if user:

            stored_password = user[3]

            # ==========================================
            # CHECK HASHED PASSWORD
            # ==========================================
            if bcrypt.checkpw(
                password.encode("utf-8"),
                stored_password.encode("utf-8")
            ):

                return {
                    "message": "Login successful",
                    "user": {
                        "id": user[0],
                        "username": user[1],
                        "email": user[2],
                         "role": user[4],
                    }
                }

        return {
            "message": "Invalid credentials"
        }

    except Exception as e:

        print("Login Error:", e)

        return {
            "message": "Login failed ❌"
        }

    finally:

        cur.close()
        conn.close()
# ==================================================
# ARTICLES API
# ==================================================
@app.route("/api/articles", methods=["GET"])
def get_articles():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title, content
        FROM articles
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    articles = [
        {
            "id": row[0],
            "title": row[1],
            "content": row[2]
        }
        for row in rows
    ]

    return {"articles": articles}
# ==================================================
# GET QUIZZES BY TOPIC
# ==================================================
@app.route("/api/quizzes/<topic>", methods=["GET"])
def get_quizzes(topic):

    username = request.args.get("username")

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        # ==========================================
        # DEFAULT PERFORMANCE
        # ==========================================
        percentage = 0

        if username:

            cur.execute("""
                SELECT score, total_questions
                FROM quiz_scores
                WHERE username = %s
                ORDER BY id DESC
                LIMIT 1
            """, (username,))

            latest = cur.fetchone()

            if latest and latest[1] > 0:
                percentage = (latest[0] / latest[1]) * 100

        # ==========================================
        # BEGINNER
        # 8 Easy + 2 Medium
        # ==========================================
        if percentage < 40:

            cur.execute("""
                (
                    SELECT
                        id,
                        question,
                        option_a,
                        option_b,
                        option_c,
                        option_d,
                        correct_answer,
                        topic,
                        difficulty
                    FROM quizzes
                    WHERE LOWER(topic)=LOWER(%s)
                    AND difficulty='Easy'
                    ORDER BY RANDOM()
                    LIMIT 8
                )

                UNION ALL

                (
                    SELECT
                        id,
                        question,
                        option_a,
                        option_b,
                        option_c,
                        option_d,
                        correct_answer,
                        topic,
                        difficulty
                    FROM quizzes
                    WHERE LOWER(topic)=LOWER(%s)
                    AND difficulty='Medium'
                    ORDER BY RANDOM()
                    LIMIT 2
                )
            """, (topic, topic))

        # ==========================================
        # INTERMEDIATE
        # 5 Easy + 5 Medium
        # ==========================================
        elif percentage < 70:

            cur.execute("""
                (
                    SELECT
                        id,
                        question,
                        option_a,
                        option_b,
                        option_c,
                        option_d,
                        correct_answer,
                        topic,
                        difficulty
                    FROM quizzes
                    WHERE LOWER(topic)=LOWER(%s)
                    AND difficulty='Easy'
                    ORDER BY RANDOM()
                    LIMIT 5
                )

                UNION ALL

                (
                    SELECT
                        id,
                        question,
                        option_a,
                        option_b,
                        option_c,
                        option_d,
                        correct_answer,
                        topic,
                        difficulty
                    FROM quizzes
                    WHERE LOWER(topic)=LOWER(%s)
                    AND difficulty='Medium'
                    ORDER BY RANDOM()
                    LIMIT 5
                )
            """, (topic, topic))

        # ==========================================
        # ADVANCED
        # 2 Easy + 4 Medium + 4 Hard
        # ==========================================
        else:

            cur.execute("""
                (
                    SELECT
                        id,
                        question,
                        option_a,
                        option_b,
                        option_c,
                        option_d,
                        correct_answer,
                        topic,
                        difficulty
                    FROM quizzes
                    WHERE LOWER(topic)=LOWER(%s)
                    AND difficulty='Easy'
                    ORDER BY RANDOM()
                    LIMIT 2
                )

                UNION ALL

                (
                    SELECT
                        id,
                        question,
                        option_a,
                        option_b,
                        option_c,
                        option_d,
                        correct_answer,
                        topic,
                        difficulty
                    FROM quizzes
                    WHERE LOWER(topic)=LOWER(%s)
                    AND difficulty='Medium'
                    ORDER BY RANDOM()
                    LIMIT 4
                )

                UNION ALL

                (
                    SELECT
                        id,
                        question,
                        option_a,
                        option_b,
                        option_c,
                        option_d,
                        correct_answer,
                        topic,
                        difficulty
                    FROM quizzes
                    WHERE LOWER(topic)=LOWER(%s)
                    AND difficulty='Hard'
                    ORDER BY RANDOM()
                    LIMIT 4
                )
            """, (topic, topic, topic))

        rows = cur.fetchall()

        quizzes = []

        for row in rows:

            quizzes.append({
                "id": row[0],
                "question": row[1],
                "option_a": row[2],
                "option_b": row[3],
                "option_c": row[4],
                "option_d": row[5],
                "correct_answer": row[6],
                "topic": row[7],
                "difficulty": row[8]
            })

        return {
            "quizzes": quizzes,
            "performance": round(percentage, 2)
        }

    except Exception as e:

        print("Quiz Error:", e)

        return {
            "quizzes": []
        }

    finally:

        cur.close()
        conn.close()
    # ==================================================
# AI QUIZ GENERATOR
# ==================================================
@app.route("/api/generate-quiz", methods=["POST"])
def generate_quiz():

    data = request.get_json()

    topic = data.get("topic", "").lower()

    generated_quiz = {}

    # ==========================================
    # PYTHON QUIZ
    # ==========================================
    if "python" in topic:

        generated_quiz = {
            "question": "What is Python mainly used for?",
            "option_a": "Web Development",
            "option_b": "Artificial Intelligence",
            "option_c": "Automation",
            "option_d": "All of the above",
            "correct_answer": "All of the above",
            "topic": "Python"
        }

    # ==========================================
    # HTML QUIZ
    # ==========================================
    elif "html" in topic:

        generated_quiz = {
            "question": "What does HTML stand for?",
            "option_a": "HyperText Markup Language",
            "option_b": "HighText Machine Language",
            "option_c": "HyperTool Multi Language",
            "option_d": "None of the above",
            "correct_answer": "HyperText Markup Language",
            "topic": "HTML"
        }

    # ==========================================
    # CSS QUIZ
    # ==========================================
    elif "css" in topic:

        generated_quiz = {
            "question": "What is CSS used for?",
            "option_a": "Database Management",
            "option_b": "Styling Web Pages",
            "option_c": "Programming Logic",
            "option_d": "AI Development",
            "correct_answer": "Styling Web Pages",
            "topic": "CSS"
        }

    # ==========================================
    # JAVASCRIPT QUIZ
    # ==========================================
    elif "javascript" in topic:

        generated_quiz = {
            "question": "What is JavaScript mainly used for?",
            "option_a": "Styling",
            "option_b": "Machine Learning",
            "option_c": "Interactive Websites",
            "option_d": "Operating Systems",
            "correct_answer": "Interactive Websites",
            "topic": "JavaScript"
        }

    # ==========================================
    # DEFAULT QUIZ
    # ==========================================
    else:

        generated_quiz = {
            "question": f"What is {topic}?",
            "option_a": "A programming concept",
            "option_b": "A database",
            "option_c": "A network protocol",
            "option_d": "An operating system",
            "correct_answer": "A programming concept",
            "topic": topic
        }

    return {
        "quiz": generated_quiz
    }
  
        # ==================================================
# AWARD BADGE HELPER
# ==================================================
def award_badge(cur, username, badge_name):

    cur.execute("""
        SELECT 1
        FROM achievements
        WHERE username = %s
        AND badge_name = %s
    """, (username, badge_name))

    if not cur.fetchone():

        cur.execute("""
            INSERT INTO achievements (
                username,
                badge_name
            )
            VALUES (%s, %s)
        """, (
            username,
            badge_name
        ))
 # ==================================================
# SAVE QUIZ SCORE API
# ==================================================
@app.route("/api/save-score", methods=["POST"])
def save_score():

    data = request.get_json()
    print(">>> NEW SAVE_SCORE VERSION IS RUNNING <<<")
    print("========== SAVE SCORE ==========")
    print(data)
    print("Username:", data.get("username"))
    print("Topic:", data.get("topic"))
    print("Score:", data.get("score"))
    print("Total Questions:", data.get("total_questions"))
    print("Answers:", data.get("answers"))

    username = data.get("username")
    topic = data.get("topic")
    score = data.get("score")
    total_questions = data.get("total_questions")
    weak_topics = data.get("weak_topics", [])
    answers = data.get("answers", [])

    conn = get_db_connection()
    cur = conn.cursor()

    try:

    
    
    # ==========================================
        # FIND USER ID
        # ==========================================

        cur.execute("""
            SELECT id
            FROM users
            WHERE username = %s
        """, (username,))

        user = cur.fetchone()

        if not user:

            return {
                "message": "User not found"
            }

        user_id = user[0]
        # ==========================================
        # CREATE QUIZ ATTEMPT
        # ==========================================

        cur.execute("""
            INSERT INTO quiz_attempts
            (
                user_id,
                topic,
                score,
                total_q,
                correct_q,
                difficulty,
                started_at,
                completed_at
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                NOW(),
                NOW()
            )
            RETURNING id
        """,
        (
            user_id,
            topic,
            score,
            total_questions,
            score,
            1
        ))

        attempt_id = cur.fetchone()[0]

        
        # ==========================================
        # SAVE EACH ANSWER
        # ==========================================

        for answer in answers:

            cur.execute("""
                INSERT INTO quiz_answers
                (
                    attempt_id,
                    question_id,
                    selected_answer,
                    is_correct,
                    time_taken_secs
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """,
            (
                attempt_id,
                answer["question_id"],
                answer["selected_answer"],
                answer["is_correct"],
                answer["time_taken_secs"]
            ))
           

        # ==========================================
        # SAVE QUIZ SCORE
        # ==========================================
        cur.execute("""
            INSERT INTO quiz_scores (
                username,
                score,
                total_questions,
                topic
            )
            VALUES (%s, %s, %s, %s)
        """, (
            username,
            score,
            total_questions,
            topic
        ))

        # ==========================================
        # SAVE WEAK TOPICS
        # ==========================================
        for topic in weak_topics:

            cur.execute("""
                SELECT id
                FROM weak_topics
                WHERE username = %s
                AND topic = %s
            """, (
                username,
                topic
                ))

            existing = cur.fetchone()

            if existing:

                cur.execute("""
                    UPDATE weak_topics
                    SET wrong_count = wrong_count + 1
                    WHERE username = %s
                    AND topic = %s
                """, (
                    username,
                    topic,
                    ))

            else:

                cur.execute("""
                    INSERT INTO weak_topics (
                        username,
                        topic,
                        wrong_count
                    )
                    VALUES (%s, %s, %s)
                """, (
                    username,
                    topic.title(),
                    1
                ))

        # ==========================================
        # COUNT USER QUIZZES
        # ==========================================
        cur.execute("""
            SELECT COUNT(*)
            FROM quiz_scores
            WHERE username = %s
        """, (username,))

        quiz_count = cur.fetchone()[0]

        # ==========================================
        # ACHIEVEMENTS
        # ==========================================
        if quiz_count >= 1:
            award_badge(cur, username, "Beginner")

        if quiz_count >= 5:
            award_badge(cur, username, "Bronze Scholar")

        if quiz_count >= 10:
            award_badge(cur, username, "Consistent Learner")

        if quiz_count >= 20:
            award_badge(cur, username, "Silver Scholar")

        if quiz_count >= 50:
            award_badge(cur, username, "Gold Scholar")

        if score == total_questions:
            award_badge(cur, username, "Quiz Master")

        conn.commit()

        return {
            "message": "Quiz analytics saved ✅"
        }

    except Exception as e:

        conn.rollback()

        print("Save Score Error:", e)

        return {
            "message": "Failed to save analytics ❌"
        }

    finally:

        cur.close()
        conn.close()
        # ==================================================
# ADAPTIVE LEARNING RECOMMENDATIONS
# ==================================================
@app.route("/api/recommendations", methods=["GET"])
def adaptive_recommendations():

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        # ==========================================
        # GET MOST MISSED TOPICS
        # ==========================================
        cur.execute("""
            SELECT topic
            FROM weak_topics
            ORDER BY wrong_count DESC
            LIMIT 3
        """)

        weak_topics = cur.fetchall()

        recommendations = []

        # ==========================================
        # FIND RECOMMENDATIONS
        # ==========================================
        for topic_row in weak_topics:

            topic = topic_row[0]

            cur.execute("""
                SELECT recommendation
                FROM recommendations
                WHERE LOWER(topic) = LOWER(%s)
                LIMIT 1
            """, (topic,))

            rec = cur.fetchone()

            if rec:

                recommendations.append({
                    "topic": topic,
                    "recommendation": rec[0]
                })

        return {
            "recommendations": recommendations
        }

    except Exception as e:

        print("Recommendation Error:", e)

        return {
            "message": "Recommendation system failed ❌"
        }

    finally:

        cur.close()
        conn.close()
        # ==================================================
# LEADERBOARD API
# ==================================================
@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
           
    SELECT
        username,
        ROUND(AVG(score), 2) AS average_score,
        COUNT(*) AS quizzes_taken
    FROM quiz_scores
    GROUP BY username
    ORDER BY average_score DESC, quizzes_taken DESC
    LIMIT 10

        """)

        rows = cur.fetchall()

        leaderboard_data = []

        rank = 1

        for row in rows:

            leaderboard_data.append({
                "rank": rank,
                "username": row[0],
                "average_score": float(row[1]),
                "quizzes_taken": row[2]
                
            })

            rank += 1

        return {
            "leaderboard": leaderboard_data
        }

    except Exception as e:

        print("Leaderboard Error:", e)

        return {
            "message": "Leaderboard failed ❌"
        }

    finally:

        cur.close()
        conn.close()
    
        # ==================================================
# ADVANCED STUDENT DASHBOARD API
# ==================================================
@app.route("/api/student-dashboard", methods=["GET"])
def student_dashboard():
    username = request.args.get("username")

    if not username:
        return {
            "message": "Username is required"
    }, 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        # ==========================================
        # TOTAL QUIZZES
        # ==========================================
        cur.execute("""
            SELECT COUNT(*)
            FROM quiz_scores
            WHERE username = %s
        """, (username,))

        total_quizzes = cur.fetchone()[0]

        # ==========================================
        # AVERAGE SCORE
        # ==========================================
        cur.execute("""
            SELECT AVG(score)
            FROM quiz_scores
          WHERE username = %s
        """, (username,))

        average_score = cur.fetchone()[0]

        if average_score is None:
            average_score = 0

        # ==========================================
        # RECENT SCORES
        # ==========================================
        cur.execute("""
            SELECT score, total_questions
            FROM quiz_scores
             WHERE username = %s
             ORDER BY id DESC
             LIMIT 5
        """, (username,))
        recent_scores = cur.fetchall()

        # ==========================================
        # WEAK TOPICS
        # ==========================================
        cur.execute("""
            SELECT
                LOWER(topic) AS topic,
                SUM(wrong_count) AS wrong_count
            FROM weak_topics
            WHERE username = %s
            GROUP BY LOWER(topic)
            ORDER BY SUM(wrong_count) DESC
            LIMIT 5
        """, (username,))

        weak_topics = cur.fetchall()

        # Format weak topic names
        formatted_weak_topics = []

        for topic in weak_topics:
            name = topic[0].lower()

            if name == "css":
                name = "CSS"
            elif name == "html":
                name = "HTML"
            elif name == "python":
                name = "Python"
            else:
                name = name.title()

            formatted_weak_topics.append({
                "topic": name,
                "wrong_count": topic[1]
            })

# ==========================================
        # TOPIC MASTERY
        # ==========================================
        cur.execute("""
            SELECT
                LOWER(topic) AS topic,
                SUM(score) AS correct,
                SUM(total_questions) AS questions,
                ROUND(
                    (SUM(score)::decimal /
                    NULLIF(SUM(total_questions),0))*100,
                    2
                ) AS mastery
            FROM quiz_scores
            WHERE username = %s
            GROUP BY LOWER(topic)
            ORDER BY LOWER(topic)
        """, (username,))

        mastery_rows = cur.fetchall()

        formatted_mastery = []

        for row in mastery_rows:
            name = row[0].lower()

            if name == "css":
                name = "CSS"
            elif name == "html":
                name = "HTML"
            elif name == "python":
                name = "Python"
            else:
                name = name.title()

            formatted_mastery.append({
                "topic": name,
                "correct": row[1],
                "questions": row[2],
                "mastery": float(row[3])
            })

        return {
            "total_quizzes": total_quizzes,
            "average_score": round(float(average_score), 2),

            "recent_scores": [
                {
                    "score": r[0],
                    "total": r[1]
                }
                for r in recent_scores
            ],

            "weak_topics": formatted_weak_topics,

            "topic_mastery": formatted_mastery
        }

    except Exception as e:
        print("Dashboard Error:", e)
        return {
            "message": "Dashboard failed ❌"
        }

    finally:
        cur.close()
        conn.close()
@app.route("/api/recommendations")
def get_recommendations():

    username = request.args.get("username")

    if not username:
        return {"message": "Username is required"}, 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                topic,
                SUM(score) AS correct,
                SUM(total_questions) AS questions,
                ROUND(
                    (SUM(score)::decimal /
                    NULLIF(SUM(total_questions),0))*100,
                    2
                ) AS mastery
            FROM quiz_scores
            WHERE username = %s
            GROUP BY topic
            ORDER BY mastery DESC
        """, (username,))

        rows = cur.fetchall()

        if not rows:
            return {
                "message": "No quiz history available."
            }

        strongest = rows[0]
        weakest = rows[-1]

        recommendation = (
            f"Practice more {weakest[0]} quizzes before moving to harder topics."
        )

        return {
            "strongest_topic": strongest[0],
            "strongest_mastery": float(strongest[3]),

            "weakest_topic": weakest[0],
            "weakest_mastery": float(weakest[3]),

            "recommendation": recommendation
        }

    finally:
        cur.close()
        conn.close()
        # ==================================================
# PDF REPORT GENERATION
# ==================================================
@app.route("/api/generate-report", methods=["GET"])
def generate_report():

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        # ==========================================
        # GET LATEST QUIZ SCORE
        # ==========================================
        cur.execute("""
            SELECT score, total_questions
            FROM quiz_scores
            ORDER BY id DESC
            LIMIT 1
        """)

        latest_score = cur.fetchone()

        # ==========================================
        # GET WEAK TOPICS
        # ==========================================
        cur.execute("""
            SELECT topic, wrong_count
            FROM weak_topics
            ORDER BY wrong_count DESC
        """)

        weak_topics = cur.fetchall()

        # ==========================================
        # CREATE PDF FILE
        # ==========================================
        pdf_path = "student_report.pdf"

        doc = SimpleDocTemplate(pdf_path)

        styles = getSampleStyleSheet()

        elements = []

        # ==========================================
        # TITLE
        # ==========================================
        elements.append(
            Paragraph(
                "Intelligent Tutoring System Report",
                styles['Title']
            )
        )

        elements.append(Spacer(1, 20))

        # ==========================================
        # QUIZ SCORE
        # ==========================================
        if latest_score:

            score_text = (
                f"Latest Quiz Score: "
                f"{latest_score[0]} / "
                f"{latest_score[1]}"
            )

        else:

            score_text = "No quiz data available."

        elements.append(
            Paragraph(score_text, styles['BodyText'])
        )

        elements.append(Spacer(1, 20))

        # ==========================================
        # WEAK TOPICS
        # ==========================================
        elements.append(
            Paragraph(
                "Weak Topics:",
                styles['Heading2']
            )
        )

        for topic in weak_topics:

            topic_text = (
                f"{topic[0]} — Wrong Answers: "
                f"{topic[1]}"
            )

            elements.append(
                Paragraph(topic_text, styles['BodyText'])
            )

        elements.append(Spacer(1, 20))

        # ==========================================
        # AI RECOMMENDATION
        # ==========================================
        recommendation = (
            "AI Recommendation: Focus more on weak topics "
            "and continue practicing quizzes."
        )

        elements.append(
            Paragraph(
                recommendation,
                styles['BodyText']
            )
        )

        # ==========================================
        # BUILD PDF
        # ==========================================
        doc.build(elements)

        return send_file(
            pdf_path,
            as_attachment=True
        )

    except Exception as e:

        print("PDF Report Error:", e)

        return {
            "message": "Failed to generate PDF ❌"
        }

    finally:

        cur.close()
        conn.close()
        # ==================================================
# WEAK TOPICS API
# ==================================================
@app.route("/api/weak-topics", methods=["GET"])
def get_weak_topics():

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                topic,
                wrong_count
            FROM weak_topics
            ORDER BY wrong_count DESC
        """)

        rows = cur.fetchall()

        weak_topics = [
            {
                "topic": row[0],
                "wrong_count": row[1]
            }
            for row in rows
        ]

        return {
            "weak_topics": weak_topics
        }

    except Exception as e:

        print("Weak Topic Error:", e)

        return {
            "weak_topics": []
        }

    finally:
        cur.close()
        conn.close()
# ==================================================
# CHATBOT API
# ==================================================
@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json()
    user_message = data.get("message", "").lower().strip()

    conn = get_db_connection()
    cur = conn.cursor()

    reply = ""

    try:

        # ==========================================
        # GET LAST CONVERSATION MEMORY
        # ==========================================
        last_chat = get_last_conversation(cur)

        conversation_context = ""

        if last_chat:

            conversation_context = (
        f"Previous User Message: {last_chat[0]}\n"
        f"Previous Bot Reply: {last_chat[1]}"
    )
    

         # ==========================================
        # GET CHATBOT RESPONSE
        # ==========================================

        reply = get_chatbot_response(cur, user_message)
    

        # ==========================================
        # SAVE CHAT HISTORY
        # ==========================================
        cur.execute("""
            INSERT INTO chats (
                user_message,
                bot_reply
            )
            VALUES (%s, %s)
        """, (
            user_message,
            reply
        ))

        # ==========================================
        # SAVE CHATBOT MEMORY
        # ==========================================
        cur.execute("""
            INSERT INTO chatbot_memory (
                user_message,
                bot_reply
            )
            VALUES (%s, %s)
        """, (
            user_message,
            reply
        ))

        conn.commit()

    except Exception as e:

        print("Chatbot Error:", e)

        reply = "Server error ❌"

    finally:

        cur.close()
        conn.close()

    return {"reply": reply}

# ==================================================
# CHAT HISTORY API
# ==================================================
@app.route("/api/history", methods=["GET"])
def history():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_message, bot_reply
        FROM chats
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    history = [
        {
            "user": row[0],
            "bot": row[1]
        }
        for row in rows
    ]

    return {"history": history}


# ==================================================
# ANALYTICS API
# ==================================================
@app.route("/api/analytics", methods=["GET"])
def analytics():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(*) FILTER (
                WHERE LOWER(user_message) LIKE '%python%'
            ) AS python_count,

            COUNT(*) FILTER (
                WHERE LOWER(user_message) LIKE '%javascript%'
            ) AS javascript_count,

            COUNT(*) FILTER (
                WHERE LOWER(user_message) LIKE '%html%'
            ) AS html_count

        FROM chats
    """)

    result = cur.fetchone()

    cur.close()
    conn.close()

    data = [
        {
            "name": "Python",
            "value": result[0]
        },
        {
            "name": "JavaScript",
            "value": result[1]
        },
        {
            "name": "HTML",
            "value": result[2]
        }
    ]

    return {"analytics": data}
    # ==================================================
# ADD ARTICLE API
# ==================================================
@app.route("/api/add-article", methods=["POST"])
def add_article():

    data = request.get_json()

    title = data.get("title")
    content = data.get("content")

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO articles (
                title,
                content
            )
            VALUES (%s, %s)
        """, (title, content))

        conn.commit()

        return {
            "message": "Article added successfully ✅"
        }

    except Exception as e:

        print("Add Article Error:", e)

        return {
            "message": "Failed to add article ❌"
        }

    finally:

        cur.close()
        conn.close()


# ==================================================
# ADD QUIZ API
# ==================================================
@app.route("/api/add-quiz", methods=["POST"])
def add_quiz():

    data = request.get_json()

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO quizzes (
                question,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer,
                topic
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("question"),
            data.get("option_a"),
            data.get("option_b"),
            data.get("option_c"),
            data.get("option_d"),
            data.get("correct_answer"),
            data.get("topic")
        ))

        conn.commit()

        return {
            "message": "Quiz added successfully ✅"
        }

    except Exception as e:

        print("Add Quiz Error:", e)

        return {
            "message": "Failed to add quiz ❌"
        }

    finally:

        cur.close()
        conn.close()
# ==================================================
# STUDENT PROFILE API
# ==================================================
@app.route("/api/student-profile/<username>", methods=["GET"])
def student_profile(username):

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        # USER INFO
        cur.execute("""
            SELECT username, email, role
            FROM users
            WHERE username = %s
        """, (username,))

        user = cur.fetchone()

        # TOTAL QUIZZES + AVERAGE + BEST SCORE
        cur.execute("""
            SELECT
                COUNT(*),
                AVG(score),
                MAX(score)
            FROM quiz_scores
            WHERE username = %s
        """, (username,))

        stats = cur.fetchone()

        return {
            "username": user[0],
            "email": user[1],
            "role": user[2],
            "total_quizzes": stats[0] or 0,
            "average_score": round(float(stats[1] or 0), 2),
            "highest_score": stats[2] or 0
        }

    except Exception as e:

        print("Profile Error:", e)

        return {
            "message": "Failed to load profile ❌"
        }

    finally:

        cur.close()
        conn.close()
# ==================================================
# ACHIEVEMENTS API
# ==================================================
@app.route("/api/achievements/<username>", methods=["GET"])
def get_achievements(username):

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT badge_name, earned_at
            FROM achievements
            WHERE username = %s
            ORDER BY earned_at DESC
        """, (username,))

        rows = cur.fetchall()

        badges = [
            {
                "badge": row[0],
                "earned_at": str(row[1])
            }
            for row in rows
        ]

        return {
            "achievements": badges
        }

    except Exception as e:

        print("Achievement Error:", e)

        return {
            "achievements": []
        }

    finally:

        cur.close()
        conn.close()
        # ==================================================
# STUDENT MANAGEMENT API
# ==================================================
@app.route("/api/students", methods=["GET"])
def get_students():

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                id,
                username,
                email,
                role,
                created_at
            FROM users
            ORDER BY id ASC
        """)

        rows = cur.fetchall()

        students = [
            {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "role": row[3],
                "created_at": str(row[4])
            }
            for row in rows
        ]

        return {
            "students": students
        }

    except Exception as e:

        print("Student Management Error:", e)

        return {
            "students": []
        }

    finally:

        cur.close()
        conn.close()
        # ==================================================
# STUDENT PERFORMANCE VIEWER API
# ==================================================
@app.route("/api/student-performance/<username>", methods=["GET"])
def student_performance(username):

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        # ==========================================
        # STUDENT STATS
        # ==========================================
        cur.execute("""
            SELECT
                COUNT(*),
                AVG(score),
                MAX(score)
            FROM quiz_scores
            WHERE username = %s
        """, (username,))

        stats = cur.fetchone()

        # ==========================================
        # ACHIEVEMENTS
        # ==========================================
        cur.execute("""
            SELECT badge_name
            FROM achievements
            WHERE username = %s
        """, (username,))

        achievements = [
            row[0]
            for row in cur.fetchall()
        ]

        # ==========================================
        # WEAK TOPICS
        # ==========================================
        cur.execute("""
            SELECT topic, wrong_count
            FROM weak_topics
            ORDER BY wrong_count DESC
            LIMIT 5
        """)

        weak_topics = [
            {
                "topic": row[0],
                "wrong_count": row[1]
            }
            for row in cur.fetchall()
        ]

        return {
            "username": username,
            "total_quizzes": stats[0] or 0,
            "average_score": round(float(stats[1] or 0), 2),
            "highest_score": stats[2] or 0,
            "achievements": achievements,
            "weak_topics": weak_topics
        }

    except Exception as e:

        print("Performance Error:", e)

        return {
            "message": "Failed to load performance ❌"
        }

    finally:

        cur.close()
        conn.close()
# ==================================================
# RUN SERVER
# ==================================================
# ==================================================
# DELETE STUDENT API
# ==================================================
@app.route("/api/delete-student/<int:user_id>", methods=["DELETE"])
def delete_student(user_id):

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            DELETE FROM users
            WHERE id = %s
        """, (user_id,))

        conn.commit()

        return {
            "message": "Student deleted successfully ✅"
        }

    except Exception as e:

        print("Delete Student Error:", e)

        return {
            "message": "Failed to delete student ❌"
        }

    finally:

        cur.close()
        conn.close()
        # ==================================================
# UPDATE USER ROLE API
# ==================================================
@app.route("/api/update-role/<int:user_id>", methods=["PUT"])
def update_role(user_id):

    data = request.get_json()

    new_role = data.get("role")

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            UPDATE users
            SET role = %s
            WHERE id = %s
        """, (new_role, user_id))

        conn.commit()

        return {
            "message": "Role updated successfully ✅"
        }

    except Exception as e:

        print("Role Update Error:", e)

        return {
            "message": "Role update failed ❌"
        }

    finally:

        cur.close()
        conn.close()
       # ==================================================
# PERFORMANCE TREND API
# ==================================================
@app.route("/api/performance-trend/<username>", methods=["GET"])
def performance_trend(username):

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        print("Username received:", username)

        cur.execute("""
            SELECT
                id,
                score
            FROM quiz_scores
            WHERE LOWER(username) = LOWER(%s)
            ORDER BY id ASC
        """, (username,))

        rows = cur.fetchall()

        print("Rows found:", rows)

        trend = []

        for row in rows:

            trend.append({
                "quiz": row[0],
                "score": row[1]
            })

        return {
            "trend": trend
        }

    except Exception as e:

        print("Trend Error:", e)

        return {
            "trend": []
        }

    finally:

        cur.close()
        conn.close()
        # ==================================================
# CERTIFICATE GENERATOR API
# ==================================================
@app.route("/api/certificate/<username>", methods=["GET"])
def generate_certificate(username):

    pdf_path = f"{username}_certificate.pdf"

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "CERTIFICATE OF ACHIEVEMENT",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 30))

    elements.append(
        Paragraph(
            f"This certificate is proudly awarded to <b>{username}</b>",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "For outstanding participation and achievement in the Intelligent Tutoring System.",
            styles["BodyText"]
        )
    )

    elements.append(Spacer(1, 30))

    elements.append(
        Paragraph(
            "Congratulations on your learning success!",
            styles["Heading3"]
        )
    )

    doc.build(elements)

    return send_file(
        pdf_path,
        as_attachment=True
    )
    # ==================================================
# TOPIC MASTERY API
# ==================================================
@app.route("/api/topic-mastery/<username>", methods=["GET"])
def topic_mastery(username):

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                topic,
                SUM(score) AS total_correct,
                SUM(total_questions) AS total_questions,
                ROUND(
                    (SUM(score)::decimal /
                    NULLIF(SUM(total_questions),0))*100,
                    2
                ) AS mastery
            FROM quiz_scores
             WHERE LOWER(username) = LOWER($s)
             GROUP BY LOWER(topic)
             ORDER BY LOWER(topic)
        """, (username,))

        rows = cur.fetchall()

        mastery = []

        for row in rows:

            mastery.append({

                "topic": row[0],
                "correct": row[1],
                "questions": row[2],
                "mastery": float(row[3])

            })

        return {
            "mastery": mastery
        }

    except Exception as e:

        print(e)

        return {
            "mastery": []
        }

    finally:

        cur.close()
        conn.close()
       # ==================================================
# STUDENT ANALYTICS API
# ==================================================
@app.route("/api/student-analytics/<username>", methods=["GET"])
def student_analytics(username):

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                ROUND(AVG(score),2),
                MAX(score),
                COUNT(*),
                ROUND(
                    SUM(score)::decimal /
                    NULLIF(SUM(total_questions),0)
                    *100,
                    2
                )
            FROM quiz_scores
            WHERE LOWER(username)=LOWER(%s)
        """, (username,))

        stats = cur.fetchone()

        return {
            "average_score": float(stats[0] or 0),
            "best_score": float(stats[1] or 0),
            "total_quizzes": stats[2] or 0,
            "accuracy": float(stats[3] or 0)
        }

    except Exception as e:

        print("Analytics Error:", e)

        return {
            "average_score": 0,
            "best_score": 0,
            "total_quizzes": 0,
            "accuracy": 0
        }

    finally:

        cur.close()
        conn.close()

        # ==================================================
# ADMIN DASHBOARD API
# ==================================================
@app.route("/api/admin/dashboard", methods=["GET"])
def admin_dashboard():

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                username,
                ROUND(AVG(score),2) AS average_score,
                MAX(score) AS best_score,
                COUNT(*) AS quizzes_taken
            FROM quiz_scores
            GROUP BY username
            ORDER BY average_score DESC
        """)

        students = []

        for row in cur.fetchall():

            students.append({
                "username": row[0],
                "average_score": float(row[1]),
                "best_score": float(row[2]),
                "quizzes_taken": row[3]
            })

        cur.execute("SELECT COUNT(DISTINCT username) FROM quiz_scores")
        total_students = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM quiz_scores")
        total_quizzes = cur.fetchone()[0]

        cur.execute("SELECT ROUND(AVG(score) * 10) FROM quiz_scores")
        average_score = cur.fetchone()[0]

        return {
            "total_students": total_students,
            "total_quizzes": total_quizzes,
            "average_score": float(average_score or 0),
            "students": students
        }

    except Exception as e:

        print(e)

        return {
            "total_students": 0,
            "total_quizzes": 0,
            "average_score": 0,
            "students": []
        }

    finally:

        cur.close()
        conn.close()
if __name__ == "__main__":
    app.run(debug=True, port=5000)