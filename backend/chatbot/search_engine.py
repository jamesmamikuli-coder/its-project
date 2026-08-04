def search_articles(cur, user_message):

    keywords = user_message.lower().split()

    for word in keywords:

        cur.execute("""
            SELECT title, content
            FROM articles
            WHERE LOWER(title) LIKE %s
               OR LOWER(content) LIKE %s
            LIMIT 1
        """, (f"%{word}%", f"%{word}%"))

        article = cur.fetchone()

        if article:
            return article

    return None


def search_quizzes(cur, user_message):

    keywords = user_message.lower().split()

    for word in keywords:

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
            WHERE LOWER(topic) LIKE %s
               OR LOWER(question) LIKE %s
            LIMIT 1
        """, (f"%{word}%", f"%{word}%"))

        quiz = cur.fetchone()

        if quiz:
            return quiz

    return None
    
    