import psycopg2


def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="its_db",
        user="postgres",
        password="admin123"
    )


def generate_explanation(question, correct_answer):
    return (
        f"The correct answer is '{correct_answer}' because it correctly answers "
        f"the question: '{question}'. Review this topic carefully to understand "
        f"the concept and improve your understanding."
    )


conn = get_db_connection()
cur = conn.cursor()

cur.execute("""
SELECT
    id,
    question,
    correct_answer
FROM quizzes
WHERE explanation IS NULL
   OR explanation = ''
""")

questions = cur.fetchall()

print(f"Found {len(questions)} questions without explanations.")

count = 0

for q in questions:

    quiz_id = q[0]
    question = q[1]
    correct_answer = q[2]

    explanation = generate_explanation(
        question,
        correct_answer
    )

    cur.execute("""
        UPDATE quizzes
        SET explanation = %s
        WHERE id = %s
    """, (explanation, quiz_id))

    count += 1

conn.commit()

print(f"Successfully updated {count} quiz explanations.")

cur.close()
conn.close()

print("Done!")