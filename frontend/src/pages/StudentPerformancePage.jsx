import { useEffect, useState } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";
function StudentPerformancePage() {

  const { username } = useParams();

  const [data, setData] = useState(null);
  const [trend, setTrend] = useState([]);

  useEffect(() => {

    axios
      .get(
        `http://127.0.0.1:5000/api/student-performance/${username}`
      )
      .then((res) => {

        setTrend(res.data.trend);
        
        setData(res.data);

      })
      .catch((err) => {

        console.log(err);

      });

  }, [username]);

  if (!data) {

    return <h2>Loading...</h2>;
  }

  return (

    <div style={{ padding: "20px" }}>

      <h1>
        👨‍🎓 Student Performance
      </h1>

      <h2>
        {data.username}
      </h2>

      <p>
        Total Quizzes:
        {" "}
        {data.total_quizzes}
      </p>

      <p>
        Average Score:
        {" "}
        {data.average_score}
      </p>

      <p>
        Highest Score:
        {" "}
        {data.highest_score}
      </p>

      <hr />

      <h2>
        🏆 Achievements
      </h2>

      {
        data.achievements.map((badge, index) => (

          <p key={index}>
            🏅 {badge}
          </p>

        ))
      }

      <hr />

      <h2>
        📚 Weak Topics
      </h2>

      {
        data.weak_topics.map((topic, index) => (

          <p key={index}>
            {topic.topic}
            {" "}
            ({topic.wrong_count})
          </p>

        ))
      }
      <hr />

<h2>
  📈 Performance Trend
</h2>

<ResponsiveContainer
  width="100%"
  height={300}
>

  <LineChart data={trend}>

    <CartesianGrid strokeDasharray="3 3" />

    <XAxis dataKey="quiz" />

    <YAxis />

    <Tooltip />

    <Line
      type="monotone"
      dataKey="score"
    />

  </LineChart>

</ResponsiveContainer>

    </div>

  );
}

export default StudentPerformancePage;