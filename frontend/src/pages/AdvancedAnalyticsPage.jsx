import { useEffect, useState } from "react";

import axios from "axios";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
  ResponsiveContainer,
} from "recharts";

function AdvancedAnalyticsPage() {

  const [analytics, setAnalytics] = useState([]);

  const [weakTopics, setWeakTopics] = useState([]);

  // ==========================================
  // LOAD DASHBOARD DATA
  // ==========================================
  useEffect(() => {

    axios
      .get("http://127.0.0.1:5000/api/student-dashboard")

      .then((res) => {

        console.log(res.data);

        // ==========================================
        // RECENT SCORES
        // ==========================================
        const scores =
          res.data.recent_scores.map(
            (item, index) => ({
              attempt: index + 1,
              score: item.score,
            })
          );

        setAnalytics(scores);

        // ==========================================
        // WEAK TOPICS
        // ==========================================
        const weak =
          res.data.weak_topics.map(
            (item) => ({
              topic: item.topic,
              wrong_count: item.wrong_count,
            })
          );

        setWeakTopics(weak);

      })

      .catch((err) => {

        console.log(err);
      });

  }, []);

  return (

    <div
      style={{
        padding: "20px",
      }}
    >

      <h1>
        📊 Advanced Analytics Dashboard
      </h1>

      {/* ========================================== */}
      {/* LINE CHART */}
      {/* ========================================== */}

      <div
        style={{
          width: "100%",
          height: "400px",
          background: "#fff",
          padding: "20px",
          marginBottom: "40px",
          borderRadius: "10px",
        }}
      >

        <h2>
          Quiz Performance Trend
        </h2>

        <ResponsiveContainer
          width="100%"
          height="100%"
        >

          <LineChart data={analytics}>

            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="attempt" />

            <YAxis />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="score"
            />

          </LineChart>

        </ResponsiveContainer>

      </div>

      {/* ========================================== */}
      {/* BAR CHART */}
      {/* ========================================== */}

      <div
        style={{
          width: "100%",
          height: "400px",
          background: "#fff",
          padding: "20px",
          borderRadius: "10px",
        }}
      >

        <h2>
          Weak Topic Analysis
        </h2>

        <ResponsiveContainer
          width="100%"
          height="100%"
        >

          <BarChart data={weakTopics}>

            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="topic" />

            <YAxis />

            <Tooltip />

            <Bar dataKey="wrong_count" />

          </BarChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
}

export default AdvancedAnalyticsPage;