import { useState, useEffect } from "react";
import axios from "axios";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

export default function AnalyticsPage() {

  const [trend, setTrend] = useState([]);

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

  }, []);

  return (

    <div style={{ padding: "20px" }}>

      <h1>
        📈 Personal Performance Trend
      </h1>

      <LineChart
        width={700}
        height={350}
        data={trend}
      >
        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="quiz" />

        <YAxis />

        <Tooltip />

        <Line
          type="monotone"
          dataKey="score"
        />

      </LineChart>

    </div>

  );
}