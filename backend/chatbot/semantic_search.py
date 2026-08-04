from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def semantic_search(cur, user_question):

    knowledge = []

    # ===========================
    # Load Articles
    # ===========================
    cur.execute("""
        SELECT title, content
        FROM articles
    """)

    for row in cur.fetchall():

        knowledge.append({
            "type": "article",
            "title": row[0],
            "content": row[1]
        })

    # ===========================
    # Load Quiz Questions
    # ===========================
    cur.execute("""
        SELECT
            topic,
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer,
            explanation,
            difficulty
        FROM quizzes
    """)

    for row in cur.fetchall():

        knowledge.append({
            "type": "quiz",
            "topic": row[0],
            "question": row[1],
            "option_a": row[2],
            "option_b": row[3],
            "option_c": row[4],
            "option_d": row[5],
            "correct_answer": row[6],
            "explanation": row[7],
            "difficulty": row[8]
        })

    if not knowledge:
        return None

    # ===========================
    # Build Search Documents
    # ===========================
    documents = []

    for item in knowledge:

        if item["type"] == "article":
            documents.append(
                item["title"] + " " + item["content"]
            )

        else:
            documents.append(
                item["topic"] + " " + item["question"]
            )

    # ===========================
    # TF-IDF
    # ===========================
    vectorizer = TfidfVectorizer()

    tfidf = vectorizer.fit_transform(
        documents + [user_question]
    )

    similarity = cosine_similarity(
        tfidf[-1],
        tfidf[:-1]
    )

    best_index = similarity.argmax()

    best_score = similarity[0][best_index]

    if best_score < 0.15:
        return None

    return knowledge[best_index]