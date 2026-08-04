import { useEffect, useState } from "react";

import { leaderboardAPI } from "../api/api";
import LoadingSpinner from "../components/LoadingSpinner";

 function LeaderboardPage() {

  const [leaders, setLeaders] = useState([]);
  const [loading, setLoading] = useState(true); 

  useEffect(() => {

   setLoading(true);

leaderboardAPI.getLeaderboard()
  .then((res) => {

    setLeaders(res.data.leaderboard);

  })
  .catch((err) => {
    console.error(err);
  })
  .finally(() => {

    setLoading(false);

  });
  }, []);
  if (loading) {
  return (
    <LoadingSpinner
      message="Loading Leaderboard..."
    />
  );
}


  return (
  <div
    style={{
      padding: "25px",
      background: "#F4F7FB",
      minHeight: "100vh",
    }}
  >
    <h1
      style={{
        color: "#1E3A8A",
        marginBottom: "10px",
      }}
    >
      🏆 Student Leaderboard
    </h1>

    <p
      style={{
        color: "#666",
        marginBottom: "30px",
      }}
    >
      Top performing students based on average quiz scores.
    </p>
    {/* ===== Top 3 Winners ===== */}

<div
  style={{
    display: "flex",
    justifyContent: "center",
    gap: "25px",
    marginBottom: "35px",
    flexWrap: "wrap",
  }}
>

  {leaders.slice(0, 3).map((leader, index) => {

    const medal =
      index === 0 ? "🥇" :
      index === 1 ? "🥈" :
      "🥉";

    const bg =
      index === 0 ? "#FFF8DC" :
      index === 1 ? "#F5F5F5" :
      "#FFE4C4";

    return (

      <div
        key={index}
        style={{
          width: index === 0 ? "260px" : "220px",
          background: bg,
          borderRadius: "20px",
          padding: index === 0 ? "35px" : "25px",
          textAlign: "center",
          boxShadow: "0 8px 20px rgba(0,0,0,.08)",
        }}
      >

        <div style={{ fontSize: index === 0 ? "70px" : "55px", }}>
          {medal}
        </div>

        <div
          style={{
            width: "70px",
            height: "70px",
            borderRadius: "50%",
            background: "#2563EB",
            color: "white",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontSize: "28px",
            fontWeight: "bold",
            margin: "15px auto",
          }}
        >
          {leader.username?.charAt(0).toUpperCase()}
        </div>

        <h2
          style={{
            margin: "10px 0",
            color: "#1E3A8A",
          }}
        >
          {leader.username}
        </h2>

        <h3
          style={{
            color: "#16A34A",
            margin: "8px 0",
          }}
        >
         {(leader.average_score * 10).toFixed(0)}%
        </h3>

        <p
          style={{
            color: "#666",
          }}
        >
          {leader.quizzes_taken} Quizzes
        </p>

      </div>

    );

  })}

</div>

    <div
      style={{
        background: "white",
        borderRadius: "20px",
        padding: "20px",
        boxShadow: "0 5px 15px rgba(0,0,0,0.08)",
      }}
    >
      <div
  style={{
    display: "grid",
    gap: "20px"
  }}
>
  {(leaders.length> 3 ? leaders.slice(3) : leaders).map((leader, index) => {

    const medal =
      leader.rank === 1
        ? "🥇"
        : leader.rank === 2
        ? "🥈"
        : leader.rank === 3
        ? "🥉"
        : "🏅";

    return (
      <div
        key={index}
        style={{
          background: "#FFFFFF",
          padding: "20px",
          borderRadius: "16px",
          boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap"
        }}
      >

        <div>
          <h2 style={{ margin: 0 }}>
            {medal} {leader.username}
          </h2>

          <p
            style={{
              margin: "6px 0",
              color: "#666"
            }}
          >
            {leader.quizzes_taken} Quiz Attempts
          </p>
        </div>

        <div
          style={{
            textAlign: "right"
          }}
        >
          <div
            style={{
              fontSize: "30px",
              fontWeight: "bold",
              color: "#2563EB"
            }}
          >
            {leader.average_score.toFixed(2)}
          </div>

          <small
            style={{
              color: "#888"
            }}
          >
            Average Score
          </small>
        </div>

      </div>
    );
  })}
</div>
    </div>
  </div>
);
}

export default LeaderboardPage;