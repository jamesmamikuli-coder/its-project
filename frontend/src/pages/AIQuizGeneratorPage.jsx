import { useState } from "react";
import { aiQuizAPI } from "../api/api";

function AIQuizGeneratorPage() {

  const [topic, setTopic] = useState("");

  const [quiz, setQuiz] = useState(null);

  const generateQuiz = async () => {

    try {

      const res =
        await aiQuizAPI.generateQuiz(topic);

      setQuiz(res.data.quiz);

    } catch (err) {

      console.log(err);
    }
  };

  return (

    <div style={{ padding: "20px" }}>

      <h1>AI Quiz Generator 🤖</h1>

      <input
        type="text"
        placeholder="Enter topic"
        value={topic}
        onChange={(e) =>
          setTopic(e.target.value)
        }
      />

      <button onClick={generateQuiz}>
        Generate Quiz
      </button>

      {
        quiz && (

          <div
            style={{
              marginTop: "20px",
              border: "1px solid #ccc",
              padding: "20px",
              borderRadius: "10px",
            }}
          >

            <h2>{quiz.question}</h2>

            <p>A. {quiz.option_a}</p>

            <p>B. {quiz.option_b}</p>

            <p>C. {quiz.option_c}</p>

            <p>D. {quiz.option_d}</p>

            <hr />

            <p>
              Correct Answer:
              {quiz.correct_answer}
            </p>

          </div>
        )
      }

    </div>
  );
}

export default AIQuizGeneratorPage;