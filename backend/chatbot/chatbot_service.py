from .search_engine import search_articles, search_quizzes
from .response_builder import (
    build_article_response,
    build_quiz_response
)
from .semantic_search import semantic_search


def get_chatbot_response(cur, user_message):

    # ------------------------------
    # Greeting
    # ------------------------------
    if "hello" in user_message or "hi" in user_message:

        return "Hello 👋 I am your intelligent study assistant."

    # ------------------------------
    # Help
    # ------------------------------
    if "help" in user_message:

        return (
            "I can help with:\n\n"
            "📚 Study materials\n"
            "📝 Quiz questions\n"
            "📈 Analytics\n"
            "💻 Programming topics\n"
            "🎓 Learning support"
        )

    # ------------------------------
    # Quiz
    # ------------------------------
    if "quiz" in user_message:

        return (
            "You can practice quizzes from the Quiz page or ask me questions about any topic."
        )

    # ------------------------------
    # Analytics
    # ------------------------------
    if "analytics" in user_message:

        return (
            "Analytics helps monitor student performance, identify weak topics, and recommend study areas."
        )

 # ------------------------------
    # Intelligent Semantic Search
    # ------------------------------
    result = semantic_search(cur, user_message)

    if result:

        if result["type"] == "article":

            return build_article_response(
                (
                    result["title"],
                    result["content"]
                )
            )

        elif result["type"] == "quiz":

            return build_quiz_response(
                (
                    result["topic"],
                    result["question"],
                    result["option_a"],
                    result["option_b"],
                    result["option_c"],
                    result["option_d"],
                    result["correct_answer"],
                    result["explanation"],
                    result["difficulty"]
                )
            )

    # ------------------------------
    # Default Response
    # ------------------------------
    return (
        "🤖 I couldn't find any matching study material.\n\n"
        "Try asking about:\n"
        "• Python\n"
        "• HTML\n"
        "• CSS\n"
        "• JavaScript\n"
        "• Database\n"
        "• Operating Systems\n"
        "• Computer Networks\n"
        "• Data Structures"
    )

    # ------------------------------
    # Default Response
    # ------------------------------
    return (
        "🤖 I couldn't find any matching study material.\n\n"
        "Try asking about:\n"
        "• Python\n"
        "• HTML\n"
        "• CSS\n"
        "• JavaScript\n"
        "• Database\n"
        "• Operating Systems\n"
        "• Computer Networks\n"
        "• Data Structures"
    )