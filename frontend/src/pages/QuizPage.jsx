import React, { useEffect, useState } from "react";
import { quizAPI } from "../api/api";
import { useNavigate } from "react-router-dom";
function QuizPage() {

  const [quizzes, setQuizzes] = useState([]);
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(null);
  const [answerDetails, setAnswerDetails] = useState([]);
const [selectedTopic, setSelectedTopic] = useState("");
const [currentQuestion, setCurrentQuestion] = useState(0); 
const [quizCompleted, setQuizCompleted] = useState(false);
const [loading, setLoading] = useState(false);
const navigate = useNavigate();
// 10 minutes (600 seconds)
const QUIZ_TIME = 600;

const [timeLeft, setTimeLeft] = useState(QUIZ_TIME);
useEffect(() => {
  if (timeLeft <= 0) {
    submitQuiz();   // Automatically submit quiz
    return;
  }

  if (score !== null) return;

    const timer = setInterval(() => {

        setTimeLeft((prev) => {

            if (prev <= 0) {
                clearInterval(timer);
                return 0;
            }

            return prev - 1;

        });

    }, 1000);

    return () => clearInterval(timer);

}, [score]);

useEffect(() => {
    setTimeLeft(QUIZ_TIME);
}, [selectedTopic]);







  // ==================================================
  // HANDLE ANSWER CHANGE
  // ==================================================
 const handleAnswer = (quizId, answer) => {

   setAnswers((prev) => ({
    ...prev,
    [quizId]: answer
}));


    const question = quizzes.find(q => q.id === quizId);

    const isCorrect = answer === question.correct_answer;

    setAnswerDetails(prev => {

        const filtered = prev.filter(
            item => item.question_id !== quizId
        );

        return [
            ...filtered,
            {
                question_id: quizId,
                selected_answer: answer,
                is_correct: isCorrect,
                time_taken_secs: 0
            }
        ];

    });

};



  // ==================================================
  // SUBMIT QUIZ
  // ==================================================
  const submitQuiz = async () => {

    let total = 0;

    let weakTopics = [];

    quizzes.forEach((quiz) => {

      if (answers[quiz.id] === quiz.correct_answer) {

        total++;

      } else {

        weakTopics.push(quiz.topic);
      }
    });

    setScore(total);
    console.log("Score =", total);
    console.table(answerDetails);
    console.log("Total answers =", answerDetails.length);
    // ==========================================
    // SAVE SCORE
    // ==========================================
    try {

    

await quizAPI.saveScore({

    username: localStorage.getItem("username"),

    topic: selectedTopic,

    score: total,

    total_questions: quizzes.length,

    weak_topics: weakTopics,

    answers: answerDetails

});

      console.log("Score saved");
      setAnswerDetails([]);

    } catch (err) {

      console.log(err);
    }
  };
  const topicIcons = {
  "Python": "🐍",
  "HTML": "🌐",
  "CSS": "🎨",
  "JavaScript": "⚡",
  "Database": "🗄️",
  "Computer Networks": "🌍",
  "Operating Systems": "💻",
  "Data Structures": "📚",
  "Algorithms": "🧩"
};
const minutes = Math.floor(timeLeft / 60);
const seconds = timeLeft % 60;
<div
  style={{
    background: "#FEF3C7",
    color: "#92400E",
    padding: "12px 20px",
    borderRadius: "12px",
    textAlign: "center",
    fontSize: "22px",
    fontWeight: "bold",
    marginBottom: "20px"
  }}
>
    ⏱️ Time Remaining: {Math.floor(timeLeft / 60)}:
    {(timeLeft % 60).toString().padStart(2, "0")}
</div>

const timerColor =
  timeLeft > 300
    ? "#2563EB"   // Blue
    : timeLeft > 120
    ? "#F59E0B"   // Orange
    : "#DC2626";  // Red
    
    
  
  return (

    <div style={{ padding: "20px" }}>

     <div
  style={{
    background: "linear-gradient(135deg, #2563EB, #1D4ED8)",
    color: "#fff",
    padding: "35px",
    borderRadius: "20px",
    marginBottom: "30px",
    textAlign: "center",
    boxShadow: "0 8px 20px rgba(37,99,235,0.25)"
  }}
>
  <h1
    style={{
      margin: 0,
      fontSize: "38px",
      fontWeight: "bold"
    }}
  >
    📝 Computer Science Quiz
  </h1>

  <p
    style={{
      marginTop: "12px",
      fontSize: "18px",
      opacity: "0.95"
    }}
  >
    Challenge yourself, improve your knowledge, and track your progress.
  </p>
</div>

      <div style={{ marginBottom: "30px" }}>

  <h2>Select a Subject</h2>

  <div
    style={{
      display: "flex",
      flexWrap: "wrap",
      gap: "12px",
      justifyContent: "center",
      marginTop: "20px"
    }}
  >

    {[
      "Python",
      "HTML",
      "CSS",
      "JavaScript",
      "Database",
      "Operating Systems",
      "Computer Networks"
    ].map((topic) => (

      <div
        key={topic}
        onClick={() => setSelectedTopic(topic)}
        style={{
    cursor: "pointer",
    background:
        selectedTopic === topic
            ? "linear-gradient(135deg,#2563EB,#1D4ED8)"
            : "#FFFFFF",

    color:
        selectedTopic === topic
            ? "#FFFFFF"
            : "#1E293B",

    borderRadius: "18px",

    padding: "20px",
    width: "160px",
    minHeight: "150px",
    textAlign: "center",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",

    boxShadow:
        selectedTopic === topic
            ? "0 10px 25px rgba(37,99,235,.35)"
            : "0 5px 15px rgba(0,0,0,.08)",

    border:
        selectedTopic === topic
            ? "3px solid #1D4ED8"
            : "2px solid #E5E7EB",

    transform:
        selectedTopic === topic
            ? "scale(1.05)"
            : "scale(1)",

    transition: "all .3s ease"
}}

      >

        <div style={{ fontSize: "40px", marginBottom: "10px" }}>
  {topicIcons[topic] || "📖"}
</div>

<div>
  {topic}
</div>
{
  selectedTopic === topic && (

    <div
      style={{
        marginTop: "12px",
        fontSize: "14px",
        fontWeight: "bold",
        color: "#E3F2FD"
      }}
    >
      ✅ Selected
    </div>

  )
}

      </div>

    ))}

  </div>

</div>
<div style={{ marginBottom: "30px" }}>

  <button
    disabled={!selectedTopic}
   onClick={() => {

    console.log("Start Quiz clicked");
    console.log("Selected Topic:", selectedTopic);

    setLoading(true);
    quizAPI.getQuizzes(selectedTopic)
    .then((res) => {

        console.log("SUCCESS");
        console.log(res);

        setCurrentQuestion(0);
        setAnswers({});
        setAnswerDetails([]);
        setScore(null);
        console.log("Before setQuizzes");

setQuizzes(res.data.quizzes);
setLoading(false);

console.log("After setQuizzes");

    })
    .catch((err) => {
        setLoading(false);

        console.log("ERROR");
        console.log(err);

    });
}}

    style={{
      background: selectedTopic
        ? "linear-gradient(135deg,#2563EB,#1D4ED8)"
        : "#CBD5E1",

      color: "#FFFFFF",

      border: "none",

      padding: "16px 40px",

      fontSize: "18px",

      fontWeight: "bold",

      borderRadius: "12px",

      cursor: selectedTopic
        ? "pointer"
        : "not-allowed",

      boxShadow: selectedTopic
        ? "0 8px 20px rgba(37,99,235,.35)"
        : "none",

      transition: "all .3s ease",

      marginTop: "15px"
    }}
>
    🚀 Start Quiz
</button>

</div>
{
loading && (

<div
    style={{
        textAlign: "center",
        marginTop: "40px",
        marginBottom: "30px"
    }}
>

<div
    style={{
        width: "70px",
        height: "70px",
        border: "8px solid #E5E7EB",
        borderTop: "8px solid #2563EB",
        borderRadius: "50%",
        margin: "0 auto",
        animation: "spin 1s linear infinite"
    }}
/>

<h2
    style={{
        marginTop: "20px",
        color: "#2563EB"
    }}
>
⏳ Loading Quiz...
</h2>

<p style={{ color: "#666" }}>
Preparing your questions...
</p>

</div>

)
}

      {!loading && score === null && quizzes.length > 0 && (


       <div
    key={quizzes[currentQuestion].id}
    style={{
        background: "#FFFFFF",
        borderRadius: "22px",
        padding: "35px",
        maxWidth: "900px",
        margin: "30px auto",
        boxShadow: "0 10px 30px rgba(0,0,0,.12)"
    }}
>
    <div
    style={{
        display: "flex",
        justifyContent: "center",
        gap: "10px",
        marginBottom: "20px",
        flexWrap: "wrap"
    }}
>

{
    quizzes.map((_, index) => (

        <div
            key={index}
            onClick={() => {
    if (
        index <= currentQuestion ||
        answers[quizzes[index].id] !== undefined
    ) {
        setCurrentQuestion(index);
    }
}}
            style={{
                width: "38px",
                height: "38px",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                fontWeight: "bold",

                background:

                    index === currentQuestion
                        ? "#2563EB"

                        : answers[quizzes[index].id] !== undefined
                        ? "#22C55E"

                        : "#E5E7EB",

                color:

                    index === currentQuestion
                        ? "#FFF"

                        : answers[quizzes[index].id] !== undefined
                        ? "#FFF"

                        : "#444",

                transition: ".3s"
            }}
        >

            {index + 1}

        </div>

    ))
}

</div>

            <div
    style={{
        width: "100%",
        background: "#ddd",
        borderRadius: "10px",
        marginBottom: "20px"
    }}
>

    <div
        style={{
            width: `${((currentQuestion + 1) / quizzes.length) * 100}%`,
            height: "18px",
            background: "#2563eb",
            borderRadius: "10px"
        }}
    />

</div>

<div
  style={{
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "25px",
    flexWrap: "wrap",
    gap: "15px"
  }}
>

  <div
    style={{
      fontWeight: "bold",
      color: "#2563EB",
      fontSize: "20px"
    }}
  >
    📖 Question {currentQuestion + 1}
  </div>

  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: "10px",
      background: "#FFFFFF",
      padding: "10px 20px",
      borderRadius: "30px",
      boxShadow: "0 4px 12px rgba(0,0,0,.12)"
    }}
  >
    <span style={{ fontSize: "22px" }}>⏳</span>

    <span
      style={{
        fontWeight: "bold",
        fontSize: "24px",
        color: timerColor,
        animation:
          timeLeft <= 60
            ? "pulse 1s infinite"
            : "none"
      }}
    >
      {String(minutes).padStart(2, "0")}:
      {String(seconds).padStart(2, "0")}
    </span>

  </div>

  <div
    style={{
      fontWeight: "bold",
      color: "#555",
      fontSize: "20px"
    }}
  >
    📝 {quizzes.length} Questions
  </div>

</div>
<h2
    style={{
        textAlign: "center",
        color: "#1E293B",
        marginBottom: "30px",
        fontSize: "30px"
    }}
>
    {quizzes[currentQuestion].question}
</h2>
           {[
    quizzes[currentQuestion].option_a,
    quizzes[currentQuestion].option_b,
    quizzes[currentQuestion].option_c,
    quizzes[currentQuestion].option_d
].map((option) => (

<div
    key={option}
    onClick={() =>
        handleAnswer(quizzes[currentQuestion].id, option)
    }
    style={{
        padding: "18px",
        marginBottom: "15px",
        borderRadius: "14px",
        border:
            answers[quizzes[currentQuestion].id] === option
                ? "3px solid #2563EB"
                : "2px solid #E5E7EB",

        background:
            answers[quizzes[currentQuestion].id] === option
                ? "#DBEAFE"
                : "#FFFFFF",

        cursor: "pointer",

        display: "flex",
        alignItems: "center",

        gap: "15px",

        transition: ".3s",

        boxShadow:
            answers[quizzes[currentQuestion].id] === option
                ? "0 8px 20px rgba(37,99,235,.25)"
                : "0 3px 10px rgba(0,0,0,.05)"
    }}
>

<input
    type="radio"
    checked={answers[quizzes[currentQuestion].id] === option}
    readOnly
/>

<span
    style={{
        fontSize: "18px",
        fontWeight: "500"
    }}
>
    {option}
</span>

</div>

))}
          </div>
        )}
      {quizzes.length > 0 && currentQuestion < quizzes.length && (

<div
    style={{
        display: "flex",
        justifyContent: "space-between",
        marginTop: "30px"
    }}
>

<button
    disabled={currentQuestion === 0}
    onClick={() => setCurrentQuestion(currentQuestion - 1)}
    style={{
    padding: "14px 30px",
    borderRadius: "12px",
    border: "none",
    fontWeight: "bold",
    fontSize: "17px",
    cursor: currentQuestion === 0 ? "not-allowed" : "pointer",

    background:
        currentQuestion === 0
            ? "#93C5FD"
            : "linear-gradient(135deg,#2563EB,#1D4ED8)",

    color: "#FFFFFF",

    boxShadow:
        currentQuestion === 0
            ? "none"
            : "0 8px 20px rgba(37,99,235,.35)",

    transition: ".3s"
}}
>
⬅ Previous
</button>

<button
    disabled={!answers[quizzes[currentQuestion].id]}
    onClick={() => {

        if (currentQuestion < quizzes.length - 1) {

            setCurrentQuestion(currentQuestion + 1);

        } else {

    const confirmSubmit = window.confirm(
        "Are you sure you want to submit your quiz?\n\nYou won't be able to change your answers after submission."
    );

    if (confirmSubmit) {
        submitQuiz();
    }

}

    }}
    style={{
        padding: "14px 30px",
        borderRadius: "12px",
        border: "none",
        fontWeight: "bold",
        fontSize: "17px",
        cursor: "pointer",
        background: "#2563EB",
        color: "#fff"
    }}
>
{currentQuestion === quizzes.length - 1
    ? "✅ Submit Quiz"
    : "Next ➡"}
</button>

</div>

)}
      

     

      {score !== null && (

<div
    style={{
        margin: "40px auto",
        maxwidth: "900",
        padding: "35px",
        background: "#FFFFFF",
        borderRadius: "20px",
        textAlign: "center",
        boxShadow: "0 10px 25px rgba(0,0,0,.12)"
    }}
>

<h2
    style={{
        color: "#2563EB",
        marginBottom: "20px"
    }}
>
🎉 Congratulations, {localStorage.getItem("username")}!
</h2>
   <p
    style={{
        marginTop: "20px",
        color: "#666",
        fontStyle: "italic"
    }}
>
Every quiz helps you improve. Keep learning and keep growing! 🚀
</p>
        
<p
    style={{
        color: "#666",
        fontSize: "18px",
        marginBottom: "25px"
    }}
>
You successfully completed the <strong>{selectedTopic}</strong> quiz.
</p>




<div
    style={{
        width: "140px",
        height: "140px",
        margin: "0 auto 25px",
        borderRadius: "50%",
        background:
    score >= quizzes.length * 0.8
        ? "linear-gradient(135deg,#10B981,#059669)"
        : score >= quizzes.length * 0.6
        ? "linear-gradient(135deg,#F59E0B,#D97706)"
        : "linear-gradient(135deg,#EF4444,#DC2626)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        color: "#fff",
        fontSize: "42px",
        fontWeight: "bold"
    }}
>
{score}/{quizzes.length}
</div>

<h3
    style={{
        color: "#444"
    }}
>
⭐ You scored {Math.round((score / quizzes.length) * 100)}%
</h3>

<p
    style={{
        fontSize: "18px",
        marginTop: "15px"
    }}
>
{
    score >= quizzes.length * 0.8
        ? "🏆 Excellent Performance!"
        : score >= quizzes.length * 0.6
        ? "👏 Good Job! Keep Improving."
        : "📚 Keep Practicing. You'll Improve!"
}
</p>
<div
    style={{
        display: "flex",
        justifyContent: "center",
        gap: "20px",
        marginTop: "30px",
        flexWrap: "wrap"
    }}
>

<button
    onClick={() => {

        setScore(null);
        setCurrentQuestion(0);
        setAnswers({});
        setAnswerDetails([]);

        quizAPI.getQuizzes(selectedTopic)
            .then((res) => {
                setQuizzes(res.data.quizzes);
            });

    }}
    style={{
        padding: "14px 28px",
        border: "none",
        borderRadius: "12px",
        background: "linear-gradient(135deg,#2563EB,#1D4ED8)",
        color: "#fff",
        fontSize: "17px",
        fontWeight: "bold",
        cursor: "pointer",
        boxShadow: "0 8px 20px rgba(37,99,235,.35)"
    }}
>
🔄 Retake Quiz
</button>

<button
    onClick={() => navigate("/dashboard")}
    style={{
        padding: "14px 28px",
        border: "none",
        borderRadius: "12px",
        background: "linear-gradient(135deg,#10B981,#059669)",
        color: "#fff",
        fontSize: "17px",
        fontWeight: "bold",
        cursor: "pointer",
        boxShadow: "0 8px 20px rgba(16,185,129,.35)"
    }}
>
🏠 Back to Dashboard
</button>

</div>

</div>

)}

    </div>
  );
}

export default QuizPage;