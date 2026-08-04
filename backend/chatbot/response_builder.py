def build_article_response(article):

    return (

        "🤖 Intelligent Tutor\n\n"

        "I found a lesson related to your question.\n\n"

        f"📚 Topic\n"
        f"{article[0]}\n\n"

        f"📖 Lesson\n"
        f"{article[1]}\n\n"

        "🎯 Learning Tip\n"
        "After reading this lesson, try answering a quiz question on this topic to reinforce your understanding."
    )
    
    
    


def build_quiz_response(quiz):

    explanation = quiz[7]

    if not explanation:
        explanation = (
            "No explanation has been added for this question yet."
        )

    return (

        "🤖 Intelligent Tutor\n\n"

        "Let's test your understanding.\n\n"

        f"📘 Topic\n"
        f"{quiz[0]}\n\n"

        f"❓ Question\n"
        f"{quiz[1]}\n\n"

        f"A. {quiz[2]}\n"
        f"B. {quiz[3]}\n"
        f"C. {quiz[4]}\n"
        f"D. {quiz[5]}\n\n"

        "🧠 Take a moment to think before reading the answer.\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        f"✅ Correct Answer\n"
        f"{quiz[6]}\n\n"

        f"💡 Explanation\n"
        f"{explanation}\n\n"

        f"⭐ Difficulty: {quiz[8]}\n\n"

        "🎯 Challenge\n"
        "Can you explain why the other options are incorrect?"
    )
    


