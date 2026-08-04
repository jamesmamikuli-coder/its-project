import { useEffect, useState } from "react";
import { quizAPI } from "../api/api";

function QuizPage() {

  const [quizzes, setQuizzes] = useState([]);
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(null);
  const [answerDetails, setAnswerDetails] = useState([]);
const [selectedTopic, setSelectedTopic] = useState("");
const [currentQuestion, setCurrentQuestion] = useState(0); 




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

console.log("After setQuizzes");

    })
    .catch((err) => {

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
        quizzes.length > 0 && ( 

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
        marginBottom: "15px",
        color: "#555",
        fontWeight: "bold"
    }}
>

<span>
    Question {currentQuestion + 1}
</span>

<span>
    {quizzes.length} Questions
</span>

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
    onChange={() => {}}
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

<button
    disabled={!answers[quizzes[currentQuestion].id]}

    onClick={() => {

        if (currentQuestion < quizzes.length - 1) {

            setCurrentQuestion(prev => prev + 1);

        } else {

            submitQuiz();

        }

    }}

    style={{
        padding: "15px 40px",
        background: answers[quizzes[currentQuestion].id]
            ? "linear-gradient(135deg,#2563EB,#1D4ED8)"
            : "#CBD5E1",

        color: "#fff",

        border: "none",

        borderRadius: "12px",

        fontWeight: "bold",

        fontSize: "18px",

        cursor: answers[quizzes[currentQuestion].id]
            ? "pointer"
            : "not-allowed",

        marginTop: "25px",

        boxShadow: answers[quizzes[currentQuestion].id]
            ? "0 8px 20px rgba(37,99,235,.35)"
            : "none"
    }}
>
    {currentQuestion === quizzes.length - 1
        ? "✅ Submit Quiz"
        : "➡️ Next Question"}

</button>

)}
      

     

      {
        score !== null && (
          <h2>Your Score: {score}</h2>
        )
      }

    </div>
  );
}

export default QuizPage;