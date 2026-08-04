import React, { useEffect, useState, useRef } from "react";
import { qaAPI } from "../api/api";

export default function ChatbotPage() {

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef(null);


  // ==================================================
  // LOAD CHAT HISTORY
  // ==================================================
  useEffect(() => {

    loadHistory();

  }, []);
  useEffect(() => {

    messagesEndRef.current?.scrollIntoView({
        behavior: "smooth"
    });

}, [messages, typing]);



  // ==================================================
  // FETCH HISTORY FROM BACKEND
  // ==================================================
  const loadHistory = async () => {

    try {

      const response = await qaAPI.getHistory();

      const history = response.data.history;

      let formattedMessages = [];

      history.reverse().forEach((chat) => {

        formattedMessages.push({
          role: "user",
          text: chat.user
        });

        formattedMessages.push({
          role: "bot",
          text: chat.bot
        });

      });

      setMessages(formattedMessages);

    } catch (error) {

      console.log(error);

    }

  };

const typeMessage = (text) => {

  return new Promise((resolve) => {

    let index = 0;

    const interval = setInterval(() => {

      index++;

      setMessages((prev) => {

        const updated = [...prev];

        updated[updated.length - 1] = {
          role: "bot",
          text: text.substring(0, index)
        };

        return updated;

      });

      if (index >= text.length) {

        clearInterval(interval);

        resolve();

      }

    }, 15);

  });

};
const askQuestion = async (question) => {

  const userMessage = {
    role: "user",
    text: question
  };

  setMessages((prev) => [...prev, userMessage]);

 try {

    // Show typing animation
    setTyping(true);

    const response = await qaAPI.askQuestion(question);

    // Make the tutor "think"
    await new Promise((resolve) =>
        setTimeout(resolve, 1000)
    );

    setTyping(false);

    // Add empty bot message
    setMessages((prev) => [
        ...prev,
        {
            role: "bot",
            text: ""
        }
    ]);

    // Type the response letter by letter
   await typeMessage(response.data.reply);

setInput("");

} catch (error) {

    console.log(error);

    setTyping(false);

    setMessages((prev) => [
        ...prev,
        {
            role: "bot",
            text: "❌ Server connection failed."
        }
    ]);

}
};
  // ==================================================
  // SEND MESSAGE
  // ==================================================
  const sendMessage = () => {

  if (!input.trim()) return;

  askQuestion(input);

};

const TypingDots = () => {

  return (
    <span
      style={{
        fontSize: "28px",
        letterSpacing: "4px",
        color: "#2563EB",
        fontWeight: "bold"
      }}
    >
      <span className="dot">•</span>
      <span className="dot">•</span>
      <span className="dot">•</span>
    </span>
  );

};
  return (

    <div style={{ padding: 20 }}>

      <div
    style={{
        marginBottom: "30px"
    }}
>

<h1
    style={{
        color: "#1E3A8A",
        marginBottom: "15px",
        fontSize: "32px",
        fontWeight: "bold"
    }}
>
🤖 Intelligent Tutor
</h1>

<p
    style={{
        color: "#6B7280",
        fontSize: "16px",
        lineHeight: "1.8",
        marginTop: "0"
    }}
>
Ask questions about programming, networking, databases, operating systems, quizzes and much more.
</p>

</div>


     {/* CHAT AREA */}

<div
  style={{
    height: "500px",
    overflowY: "auto",
    padding: "20px",
    background: "#F4F7FB",
    borderRadius: "20px",
    border: "1px solid #E5E7EB",
    boxShadow: "0 4px 15px rgba(0,0,0,0.08)",
    marginBottom: "20px"
  }}
>

  {messages.map((msg, index) => (

    <div
      key={index}
      style={{
        display: "flex",
        justifyContent:
          msg.role === "user"
            ? "flex-end"
            : "flex-start",
        marginBottom: "18px"
      }}
    >

      <div
        style={{
          maxWidth: "75%",
          background:
            msg.role === "user"
              ? "#2563EB"
              : "#FFFFFF",

          color:
            msg.role === "user"
              ? "#FFFFFF"
              : "#222",

          padding: "14px 18px",

          borderRadius:
            msg.role === "user"
              ? "20px 20px 5px 20px"
              : "20px 20px 20px 5px",

          boxShadow:
            "0 2px 10px rgba(0,0,0,0.08)",

          whiteSpace: "pre-wrap",

          lineHeight: "1.6"
        }}
      >

        <div
          style={{
            fontWeight: "bold",
            marginBottom: "8px",
            fontSize: "14px"
          }}
        >
          {msg.role === "user"
            ? "👤 You"
            : "🤖 Intelligent Tutor"}
            {typing && (

<div
    style={{
        display: "flex",
        justifyContent: "flex-start",
        marginBottom: "18px"
    }}
>

<div
    style={{
        background: "#FFFFFF",
        padding: "14px 18px",
        borderRadius: "20px 20px 20px 5px",
        boxShadow: "0 2px 10px rgba(0,0,0,0.08)"
    }}
>

<div
    style={{
        fontWeight: "bold",
        marginBottom: "8px"
    }}
>
🤖 Intelligent Tutor
</div>

<TypingDots/>

</div>

</div>

)}
<div ref={messagesEndRef}></div>



        </div>

        {msg.text}

      </div>

    </div>

  ))}

</div>

<div
  style={{
    display: "flex",
    flexWrap: "wrap",
    gap: "10px",
    marginBottom: "15px"
  }}
>

{[
"🐍 Python",
"🌐 HTML",
"🎨 CSS",
"☕ JavaScript",
"🗄 Database",
"💻 Operating Systems",
"🌍 Networking",
"⚙ Algorithms",
"🧠 Data Structures"
].map((topic, index)=>(

<button
key={index}

onClick={() => {

  askQuestion(
    `Teach me ${topic.replace(/[^a-zA-Z ]/g, "")} programming`
  );

}}


style={{
  background: "#F8FAFC",
  border: "1px solid #CBD5E1",
  color: "#1E3A8A",
  padding: "10px 18px",
  borderRadius: "25px",
  cursor: "pointer",
  fontWeight: "600",
  fontSize: "15px",
  transition: "all 0.25s ease",
  boxShadow: "0 2px 6px rgba(0,0,0,0.08)"
}}

onMouseEnter={(e)=>{
    e.target.style.background="#2563EB";
    e.target.style.color="white";
    e.target.style.transform="translateY(-2px)";
}}

onMouseLeave={(e)=>{
    e.target.style.background="#F8FAFC";
    e.target.style.color="#1E3A8A";
    e.target.style.transform="translateY(0)";
}}
>

{topic}

</button>

))}

</div>

     
<div
  style={{
    display: "flex",
    gap: "10px"
  }}
>

<input
    type="text"
    placeholder="Ask me anything about Computer Science..."
    value={input}
    onChange={(e) => setInput(e.target.value)}

    onKeyDown={(e) => {
      if (e.key === "Enter") {
        sendMessage();
      }
    }}

    style={{
      flex: 1,
      padding: "15px",
      borderRadius: "12px",
      border: "1px solid #D1D5DB",
      fontSize: "16px",
      outline: "none"
    }}
/>

<button
    onClick={sendMessage}

    style={{
      background: "#2563EB",
      color: "white",
      border: "none",
      borderRadius: "12px",
      padding: "0 25px",
      cursor: "pointer",
      fontWeight: "bold",
      fontSize: "16px"
    }}
>
    🚀 Send
</button>

</div>


    </div>
  );
}