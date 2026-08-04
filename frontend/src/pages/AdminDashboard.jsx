import { useEffect, useState } from "react";
import axios from "axios";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function AdminDashboard() {

  const [dashboard, setDashboard] = useState({
    total_students: 0,
    total_quizzes: 0,
    average_score: 0,
    students: [],
  });

  useEffect(() => {

    axios
      .get("http://127.0.0.1:5000/api/admin/dashboard")
      .then((res) => {
        setDashboard(res.data);
      })
      .catch(console.error);

  }, []);

  const cardStyle = {
    background: "white",
    borderRadius: "18px",
    padding: "25px",
    textAlign: "center",
    boxShadow: "0 5px 15px rgba(0,0,0,.08)",
  };
   return (

<div style={{ padding: "30px" }}>

<h1 style={{ color:"#1E3A8A" }}>
👨‍💼 Admin Dashboard
</h1>

<div
style={{
display:"grid",
gridTemplateColumns:"repeat(3,1fr)",
gap:"20px",
marginTop:"25px"
}}
>

<div style={cardStyle}>
<h3>Total Students</h3>
<h1>{dashboard.total_students}</h1>
</div>

<div style={cardStyle}>
<h3>Total Quizzes</h3>
<h1>{dashboard.total_quizzes}</h1>
</div>

<div style={cardStyle}>
<h3>Average Score</h3>
<h1>{dashboard.average_score}%</h1>
</div>

</div>
<div
style={{
marginTop:"30px",
background:"white",
padding:"25px",
borderRadius:"20px",
boxShadow:"0 5px 15px rgba(0,0,0,.08)"
}}
>

<h2>📊 Student Performance</h2>

<ResponsiveContainer width="100%" height={350}>

<BarChart data={dashboard.students}>

<CartesianGrid strokeDasharray="3 3"/>

<XAxis dataKey="username"/>

<YAxis/>

<Tooltip/>

<Bar
dataKey="average_score"
fill="#2563EB"
/>

</BarChart>

</ResponsiveContainer>

</div>
<div
style={{
marginTop:"30px",
background:"white",
padding:"20px",
borderRadius:"20px",
boxShadow:"0 5px 15px rgba(0,0,0,.08)"
}}
>

<h2>👨‍🎓 Students</h2>

<table
style={{
width:"100%",
borderCollapse:"collapse"
}}
>

<thead>

<tr style={{background:"#2563EB",color:"white"}}>

<th>Student</th>

<th>Average</th>

<th>Best</th>

<th>Quizzes</th>

<th>Status</th>

</tr>

</thead>

<tbody>

{dashboard.students.map((student,index)=>(

<tr key={index}>

<td>{student.username}</td>

<td>{student.average_score}/10</td>

<td>{student.best_score}</td>

<td>{student.quizzes_taken}</td>

<td>

{student.average_score>=80
?"🟢 Excellent"
:student.average_score>=60
?"🟡 Good"
:"🔴 Needs Help"}

</td>

</tr>

))}

</tbody>

</table>

</div>

</div>

);
}
  
  