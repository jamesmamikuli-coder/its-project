def get_last_conversation(cur):

    cur.execute("""
        SELECT user_message, bot_reply
        FROM chatbot_memory
        ORDER BY id DESC
        LIMIT 1
    """)

    return cur.fetchone()
    


    
    
    