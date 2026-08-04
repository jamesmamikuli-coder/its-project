import { useState, useEffect } from "react";
import axios from "axios";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from "recharts";

export default function AnalyticsPage() {

  const COLORS = [
  "#2563EB",
  "#16A34A",
  "#F59E0B",
  "#EF4444",
  "#8B5CF6",
];

const [analytics, setAnalytics] = useState({
  average_score: 0,
  best_score: 0,
  total_quizzes: 0,
  accuracy: 0,
});


  const [trend, setTrend] = useState([]);

   const cardStyle = {
  background: "white",
  borderRadius: "16px",
  padding: "25px",
  boxShadow: "0 5px 15px rgba(0,0,0,.08)",
  textAlign: "center",
};
 const topicData = [
  { topic: "Programming", score: 82 },
  { topic: "Database", score: 76 },
  { topic: "Networking", score: 65 },
  { topic: "Algorithms", score: 88 },
  { topic: "Operating System", score: 73 },
];

const quizDistribution = [
  { name: "Passed", value: 14 },
  { name: "Failed", value: 3 },
];

  useEffect(() => {



    const username =
      localStorage.getItem("username");

    axios
      .get(
        `http://127.0.0.1:5000/api/performance-trend/${username}`
      )
      .then((res) => {

        setTrend(res.data.trend);

      })
      .catch((err) => {

        console.error(err);

      });
      axios
  .get(`http://127.0.0.1:5000/api/student-analytics/${username}`)
  .then((res) => {
    setAnalytics(res.data);
  })
  .catch((err) => {
    console.error(err);
  });


  }, []);

 

 return (

<div style={{ padding: "30px" }}>

<h1 style={{ color:"#1E3A8A" }}>
📊 Learning Analytics
</h1>

<p style={{color:"#666"}}>
Track your learning progress and performance.
</p>

<div
style={{
display:"grid",
gridTemplateColumns:"repeat(4,1fr)",
gap:"20px",
marginTop:"25px"
}}
>

<div style={cardStyle}>
<h3>Average Score</h3>
<h1>{analytics.average_score}%</h1>
</div>

<div style={cardStyle}>
<h3>Best Score</h3>
<h1>{analytics.best_score}%</h1>
</div>

<div style={cardStyle}>
<h3>Total Quizzes</h3>
<h1>{analytics.total_quizzes}</h1>
</div>

<div style={cardStyle}>
<h3>Accuracy</h3>
<h1>{analytics.accuracy}%</h1>
</div>

</div>

<div
  style={{
    background: "white",
    borderRadius: "20px",
    padding: "25px",
    marginTop: "30px",
    boxShadow: "0 5px 15px rgba(0,0,0,.08)",
  }}
>

  <h2 style={{ color: "#1E3A8A" }}>
    📈 Performance Trend
  </h2>

  <ResponsiveContainer width="100%" height={350}>
    <LineChart data={trend}>

      <CartesianGrid strokeDasharray="3 3" />

      <XAxis dataKey="quiz" />

      <YAxis />

      <Tooltip />

      <Legend />

      <Line
        type="monotone"
        dataKey="score"
        stroke="#2563EB"
        strokeWidth={3}
      />

    </LineChart>
  </ResponsiveContainer>

</div>

<div
  style={{
    display: "grid",
    gridTemplateColumns:
    "repeat(auto-fit,minmax(350px,1fr))", 
    gap: "25px",
    marginTop: "30px",
  }}
>

  {/* Topic Performance */}

  <div
    style={{
      background: "white",
      borderRadius: "20px",
      padding: "25px",
      boxShadow: "0 5px 15px rgba(0,0,0,.08)",
    }}
  >

    <h2 style={{ color:"#1E3A8A" }}>
      📚 Topic Performance
    </h2>

    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={topicData}>

        <CartesianGrid strokeDasharray="3 3"/>

        <XAxis dataKey="topic"/>

        <YAxis/>

        <Tooltip/>

        <Bar
          dataKey="score"
          fill="#2563EB"
        />

      </BarChart>
    </ResponsiveContainer>

  </div>

  {/* Quiz Distribution */}

  <div
    style={{
      background:"white",
      borderRadius:"20px",
      padding:"25px",
      boxShadow:"0 5px 15px rgba(0,0,0,.08)"
    }}
  >

    <h2 style={{color:"#1E3A8A"}}>
      🥧 Quiz Distribution
    </h2>

    <ResponsiveContainer width="100%" height={320}>
      <PieChart>

        <Pie
          data={quizDistribution}
          dataKey="value"
          nameKey="name"
          outerRadius={100}
          label
        >

          {quizDistribution.map((entry,index)=>(
            <Cell
              key={index}
              fill={COLORS[index % COLORS.length]}
            />
          ))}

        </Pie>

        <Tooltip/>

      </PieChart>

    </ResponsiveContainer>

  </div>

</div>


</div>



  );
}