import { useEffect, useState } from "react";
import { dashboardAPI } from "../api/api";
import { reportAPI } from "../api/api";
import { recommendationAPI } from "../api/api";
import LoadingSpinner from "../components/LoadingSpinner";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LabelList
} from "recharts";

function DashboardPage() {

  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true); 
  const chartData =
     (dashboard?.recent_scores || []).map((item, index) => ({
        quiz: `Quiz ${index + 1}`,
        score: Number(item?.score || 0),
        total: Number(item?.total_questions || item?.total || 10)
      }))
      ||
     [];
  const [recommendations, setRecommendations] =useState([]);

const downloadReport = async () => {

  try {

    const response =
      await reportAPI.generateReport();

    const url =
      window.URL.createObjectURL(
        new Blob([response.data])
      );

    const link =
      document.createElement("a");

    link.href = url;

    link.setAttribute(
      "download",
      "student_report.pdf"
    );

    document.body.appendChild(link);

    link.click();

  } catch (err) {

    console.log(err);
  }
};
 useEffect(() => {

    const username = localStorage.getItem("username");

    setLoading(true);

    dashboardAPI
        .getDashboard(username)
        .then((res) => {

            console.log("Dashboard:", res.data);

            setDashboard(res.data);

        })
        .catch((err) => {

            console.error(err);

        })
        .finally(() => {

            setLoading(false);

        });
        
        recommendationAPI
    .getRecommendations(localStorage.getItem("username"))
    .then((res) => {

        setRecommendations(res.data.recommendations);

    })
    .catch((err) => {

        console.log(err);

    });

}, []);

  



  if (loading) {
  return (
    <LoadingSpinner
      message="Loading Dashboard..."
    />
  );
}

if (!dashboard) {
  return <p>No dashboard data found.</p>;
}

  const topicMastery =
  dashboard?.topic_mastery || [];
 const strongestTopic =
    topicMastery.length > 0
        ? topicMastery.reduce(
              (best, topic) =>
                  topic.mastery > best.mastery ? topic : best
          )
        : null;
        

     const weakestTopic =
    topicMastery.length > 0
        ? topicMastery.reduce(
              (worst, topic) =>
                  topic.mastery < worst.mastery ? topic : worst
          )
        : null;
        const hour = new Date().getHours();

let greeting = "🌞 Good Morning";

if (hour >= 12 && hour < 17) {
    greeting = "☀️ Good Afternoon";
} else if (hour >= 17) {
    greeting = "🌙 Good Evening";
}


  return (

<div
  style={{
    padding: "30px",
    background: "#F4F7FB",
    minHeight: "100vh",
    maxWidth: "1400px",
    width: "100%",
    margin: "0 auto",
    
    
  }}
>
 <div
  style={{
    textAlign: "center",
    marginBottom: "30px"
  }}
>

  <div
  style={{
    background: "linear-gradient(135deg,#2563EB,#1D4ED8)",
    color: "#fff",
    borderRadius: "20px",
    padding: "35px 40px",
    marginBottom: "40px",
    boxShadow: "0 12px 30px rgba(37,99,235,.30)",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: "20px",
    fontSize: "38px",
  }}
>

  <div>

    <h1
      style={{
        margin: 0,
        fontSize: "34px",
        fontWeight: "700",
        color: "#FFFFFF"
      }}
    >
      {greeting}, {localStorage.getItem("username")}! 👋
    </h1>

    <p
      style={{
        marginTop: "12px",
        fontSize: "18px",
        opacity: 0.95
      }}
    >
      Ready to continue your learning journey today?
    </p>

    <p
      style={{
        marginTop: "10px",
        fontSize: "15px",
        opacity: 0.9
      }}
    >
      📅 {new Date().toDateString()}
    </p>

  </div>

  <button
    onClick={downloadReport}
    style={{
      background: "#FFFFFF",
      color: "#2563EB",
      padding: "12px 24px",
      border: "none",
      borderRadius: "10px",
      cursor: "pointer",
      fontWeight: "bold",
      fontSize: "15px",
      transition: "0.3s"
    }}
    onMouseEnter={(e)=>{
      e.target.style.transform="translateY(-3px)";
      e.target.style.boxShadow="0 10px 20px rgba(0,0,0,.20)";
    }}
    onMouseLeave={(e)=>{
      e.target.style.transform="translateY(0)";
      e.target.style.boxShadow="none";
    }}
  >
    📄 Download PDF Report
  </button>
  </div>

</div>


  {/* Statistics Cards */}

  <div
    style={{
      display: "flex",
      flexWrap: "wrap",
      gap: "20px",
      justifyContent: "center",
      marginBottom: "30px"
    }}
  >

    {/* Total Quizzes */}

    <div
      style={{
    flex: "1 1 280px",
    background: "#FFFFFF",
    borderRadius: "20px",
    padding: "35px",
    textAlign: "center",
    transform: "translateY(-6px)",
    boxShadow: "0 12px 25px rgba(0,0,0,0.15)",
    transition: "0.3s",
    cursor: "pointer",
    borderTop: "5px solid #2563EB"
}}

onMouseEnter={(e)=>{
    e.currentTarget.style.transform="translateY(-8px)";
    e.currentTarget.style.boxShadow="0 18px 35px rgba(37,99,235,.25)";
}}

onMouseLeave={(e)=>{
    e.currentTarget.style.transform="translateY(0)";
    e.currentTarget.style.boxShadow="0 8px 25px rgba(0,0,0,.08)";
}}

    >

      <div
style={{
    fontSize:"55px",
    marginBottom:"12px"
}}
>
📚
</div>


      <h3
style={{
    color:"#6B7280",
    fontSize:"18px",
    marginBottom:"10px",
    background: "#fff"
}}
>
Total Quizzes
</h3>


     <h1
style={{
    color:"#2563EB",
    fontSize:"52px",
    margin:0,
    fontWeight:"bold"
}}
      >
        {dashboard.total_quizzes}
      </h1>

    </div>

    {/* Average Score */}

    <div
     style={{
    flex: "1 1 280px",
    background: "#FFFFFF",
    borderRadius: "20px",
    padding: "35px",
    textAlign: "center",
    transform: "translateY(-6px)",
    boxShadow: "0 12px 25px rgba(0,0,0,0.15)",
    transition: "0.3s",
    cursor: "pointer",
    borderTop: "5px solid #10B981"
}}

onMouseEnter={(e)=>{
    e.currentTarget.style.transform="translateY(-8px)";
    e.currentTarget.style.boxShadow="0 18px 35px rgba(37,99,235,.25)";
}}

onMouseLeave={(e)=>{
    e.currentTarget.style.transform="translateY(0)";
    e.currentTarget.style.boxShadow="0 8px 25px rgba(0,0,0,.08)";
}}
    >

      <div
style={{
    fontSize:"55px",
    marginBottom:"12px"
}}
>🎯</div>

      <h3
style={{
    color:"#10B981",
    fontSize:"18px",
    marginBottom:"10px",
    background: "#fff"
}}
>
        Average Score
      </h3>

      <h1
style={{
    color:"#10B981",
    fontSize:"52px",
    margin:0,
    fontWeight:"bold"
}}
>
        {dashboard.average_score}/10
      </h1>

    </div>

  </div>

  {/* Recent Quiz Performance Card */}

  <div
  style={{
    background: "#fff",
    padding: "25px",
    borderRadius: "20px",
    boxShadow: "0 8px 20px rgba(0,0,0,0.08)",
    marginTop: "25px"
  }}
>
    <div
      style={{
        marginBottom: "20px"
      }}
    >

      <h2
        style={{
          color: "#1E3A8A",
          fontSize: "clamp(22px, 3vw, 30px)",
          marginBottom: "5px"
        }}
      >
        📊 Recent Quiz Performance (Last 5 Attempts)
      </h2>

      <p
        style={{
          color: "#6B7280",
           fontSize: "clamp(22px, 3vw, 30px)",
          marginBottom: "20px"
        }}
      >
        Track how your scores have improved over your last five quizzes.
      </p>
      <p
style={{
textAlign:"center",
color:"#6B7280",
marginTop:"15px",
fontSize:"14px"
}}
>
Keep practicing to improve your average score.
</p>

    </div>


<div
  style={{
   width: "100%",
   height: "360px"
  }}
>

<ResponsiveContainer
  width="100%"
  height={380}
>

<BarChart
  data={chartData}
>

  <CartesianGrid
  stroke="#E5E7EB" 
  strokeDasharray="5 5" />

  <XAxis
    dataKey="quiz"
    tick={{
        fill: "#475569",
        fontWeight: "bold"
    }}
/>

  <YAxis
  domain={[0, 10]}
    tick={{
        fill: "#555"
    }}
/>



 <Tooltip
    formatter={(value, name, props) => [
        `${value}/${props.payload.total}`,
        "Score"
    ]}
    cursor={{
        fill: "#EEF4FF"
    }}
    contentStyle={{
        borderRadius: "12px",
        border: "none",
        boxShadow: "0 4px 12px rgba(0,0,0,0.15)"
    }}
/>

 <Bar
    dataKey="score"
    fill="#2563EB"
    radius={[10, 10, 0, 0]}
    radius={[10, 10, 0, 0]}
    isAnimationActive={false}
    animationDuration={1200}
    animationEasing="ease-out"
>

    <LabelList
        dataKey="score"
        position="top"
        fill="#1E3A8A"
        fontWeight="bold"
        fontSize={14}
    />

</Bar>

</BarChart>
</ResponsiveContainer>
</div>
</div>


      <br />
      <hr />

<div
  style={{
    background: "#fff",
    padding: "20px",
    borderRadius: "15px",
    boxShadow: "0 4px 10px rgba(0,0,0,0.08)",
    marginTop: "30px",
  }}
>
  <h2
    style={{
      color: "#1E3A8A",
      marginBottom: "20px",
      textAlign: "center",
    }}
  >
    🏆 Learning Summary
  </h2>

  <div
    style={{
      display: "flex",
      gap: "20px",
      flexWrap: "wrap",
      justifyContent: "space-between",
    }}
  >
    {/* Strongest Topic */}
    <div
      style={{
        flex: 1,
        minWidth: "250px",
        background: "#E8F5E9",
        padding: "20px",
        borderRadius: "12px",
      }}
    >
      <h3 style={{ color: "#2E7D32" }}>✅ Strongest Topic</h3>

      <h2>{strongestTopic ? strongestTopic.topic : "N/A"}</h2>

     <p
  style={{
    fontSize: "30px",
    fontWeight: "bold",
    color: "#2E7D32",
    marginTop: "15px"
  }}
>
  {strongestTopic ? `${strongestTopic.mastery}%` : "0%"}
</p>
    </div>

    {/* Weakest Topic */}
    <div
      style={{
        flex: 1,
        minWidth: "250px",
        background: "#FFEBEE",
        padding: "20px",
        borderRadius: "12px",
      }}
    >
      <h3 style={{ color: "#C62828" }}>📉 Needs Improvement</h3>

      <h2>{weakestTopic ? weakestTopic.topic : "N/A"}</h2>

      <p
  style={{
    fontSize: "30px",
    fontWeight: "bold",
    color: "#C62828",
    marginTop: "15px"
  }}
>
  {weakestTopic ? `${weakestTopic.mastery}%` : "0%"}
</p>
    </div>
  </div>
</div>
      
<div
  style={{
    background: "#fff",
    padding: "20px",
    borderRadius: "12px",
    marginBottom: "25px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
  }}
>

<h2
  style={{
    textAlign: "center",
    margin: "30px 0 20px",
    color: "#1E3A8A",
  }}
>
    ⚠️ Weak Topics
</h2>

<div
  style={{
    display: "flex",
    flexDirection: "column",
    gap: "15px",
  }}
>
  {(dashboard.weak_topics || []).map((item, index) => (
    <div
      key={index}
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        background: "#FFF8E1",
        padding: "15px 20px",
        borderLeft: "6px solid #F59E0B",
        borderRadius: "10px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
      }}
    >
      <span
        style={{
          fontWeight: "600",
          fontSize: "18px",
        }}
      >
        📘 {item.topic}
      </span>

      <span
        style={{
          color: "#D32F2F",
          fontWeight: "bold",
          fontSize: "18px",
        }}
      >
        {item.wrong_count} mistakes
      </span>
    </div>
  ))
  }
</div>
</div>
      
      <hr />
      
<div
  style={{
    background: "#fff",
    padding: "20px",
    borderRadius: "12px",
    marginBottom: "25px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
  }}
>

<h2>📚 Topic Mastery</h2>

{
  (dashboard.topic_mastery || []).map((topic) => (

    <div
      key={topic.topic}
      style={{ marginBottom: "20px" }}
    >

      <div
        style={{
          background: "#fff",
    padding: "20px",
    borderRadius: "12px",
    marginBottom: "25px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
        }}
      >

        <div
    style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "8px"
    }}
>

    <strong
        style={{
            color: "#1F2937",
            fontSize: "16px"
        }}
    >
        {topic.topic}
    </strong>

    <strong
        style={{
            color: "#2563EB",
            fontSize: "16px"
        }}
    >
        {topic.mastery}%
    </strong>

</div>



      </div>

      <div
        style={{
          width: "100%",
          height: "20px",
          background: "#E0E0E0",
          borderRadius: "20px",
          overflow: "hidden"
        }}
      >

        <div
          style={{
            width: `${topic.mastery}%`,
            height: "100%",
            background:
              topic.mastery >= 80
                ? "#4CAF50"
                : topic.mastery >= 60
                ? "#FF9800"
                : "#F44336",
            transition: "0.5s"
          }}
        />

      </div>

    </div>

  ))
}

</div>
<div
  style={{
    background: "#fff",
    padding: "20px",
    borderRadius: "12px",
    marginBottom: "25px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
  }}
>

<h2>🤖 AI Study Recommendations</h2>

{
  (recommendations || []).length === 0 ? (

    <p
      style={{
        color: "#666",
        fontStyle: "italic"
      }}
    >
      No AI recommendations available yet.
    </p>

  ) : (

    (recommendations || []).map((item, index) => (

      <div
    key={index}
    style={{
        background: "#FFFFFF",
        borderRadius: "15px",
        padding: "20px",
        marginBottom: "20px",
        borderLeft: "6px solid #2563EB",
        boxShadow: "0 4px 12px rgba(0,0,0,0.08)"
    }}
>

    <h3
        style={{
            color: "#1E3A8A",
            marginBottom: "12px"
        }}
    >
        📘 {item.topic}
    </h3>

    <p
        style={{
            color: "#444",
            marginBottom: "8px",
            fontWeight: "bold"
        }}
    >
        💡 Recommendation
    </p>

    <p
        style={{
            color: "#666",
            lineHeight: "1.7"
        }}
    >
        {item.recommendation}
    </p>

</div>

    ))

  )
}

</div>
</div>

    
  );

}
export default DashboardPage;