import { useState } from "react";
import { Link } from "react-router-dom";
import { authAPI } from "../api/api";
import toast from "react-hot-toast";

function RegisterPage() {

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
const [showPassword, setShowPassword] = useState(false);
const [loading, setLoading] = useState(false);

 const handleRegister = async () => {
    setLoading(true);
    if (!username.trim()) {
    toast.error("Username is required");
    return;
}

if (username.length < 3) {
    toast.error("Username must be at least 3 characters");
    return;
}

if (!email.includes("@")) {
    toast.error("Enter a valid email");
    return;
}

if (password.length < 6) {
    toast.error("Password must be at least 6 characters");
    return;
}


    try {

      const res = await authAPI.register({
        username,
        email,
        password,
      });

      toast.success(res.data.message);

    } catch (err) {
      toast.error("Registration failed");

      console.log(err);
    }
  };

  return (

    <div
    style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "linear-gradient(135deg,#2563EB,#1D4ED8)",
        padding: "20px"
    }}
>
<div
    style={{
        background: "#FFFFFF",
        padding: "40px",
        borderRadius: "22px",
        width: "100%",
        maxWidth: "430px",
        boxShadow: "0 15px 35px rgba(0,0,0,.25)"
    }}
>
      <h1
    style={{
        textAlign: "center",
        color: "#2563EB",
        fontSize: "34px",
        marginBottom: "10px"
    }}
>
🎓 Intelligent Tutoring System
</h1>

<p
    style={{
        textAlign: "center",
        color: "#666",
        marginBottom: "35px"
    }}
>
Create your student account and start learning.
</p>
     <input
    type="text"
    placeholder="👤 Username"
    value={username}
    onChange={(e) => setUsername(e.target.value)}
    style={{
        width: "100%",
        padding: "15px",
        marginBottom: "18px",
        borderRadius: "12px",
        border: "2px solid #E5E7EB",
        fontSize: "16px",
        boxSizing: "border-box"
    }}
/>
      <br /><br />

      <input
    type="email"
    placeholder="📧 Email Address"
    value={email}
    onChange={(e) => setEmail(e.target.value)}
    style={{
        width: "100%",
        padding: "15px",
        marginBottom: "18px",
        borderRadius: "12px",
        border: "2px solid #E5E7EB",
        fontSize: "16px",
        boxSizing: "border-box"
    }}
/>


      <br /><br />

     <div
    style={{
        position: "relative",
        marginBottom: "25px"
    }}
>

<input
    type={showPassword ? "text" : "password"}
    placeholder="🔒 Password"
    value={password}
    onChange={(e) => setPassword(e.target.value)}
    style={{
        width: "100%",
        padding: "15px",
        borderRadius: "12px",
        border: "2px solid #E5E7EB",
        fontSize: "16px",
        boxSizing: "border-box"
    }}
/>

<span
    onClick={() => setShowPassword(!showPassword)}
    style={{
        position: "absolute",
        right: "15px",
        top: "50%",
        transform: "translateY(-50%)",
        cursor: "pointer",
        fontSize: "20px"
    }}
>
    {showPassword ? "🙈" : "👁️"}
</span>

</div>


      <br /><br />

     <button
    onClick={handleRegister}
    disabled={loading}
    style={{
        width: "100%",
        padding: "15px",
        background: "linear-gradient(135deg,#2563EB,#1D4ED8)",
        color: "#FFFFFF",
        border: "none",
        borderRadius: "12px",
        fontSize: "18px",
        fontWeight: "bold",
        cursor: "pointer",
        boxShadow: "0 8px 20px rgba(37,99,235,.35)"
    }}
>
    {loading ? "⏳ Creating Account..." : "📝 Register"}
</button>
<div
    style={{
        textAlign: "center",
        marginTop: "20px"
    }}
>

<p>

Already have an account?

<Link
    to="/login"
    style={{
        color: "#2563EB",
        fontWeight: "bold",
        textDecoration: "none",
        marginLeft: "6px"
    }}
>

Login

</Link>

</p>

</div>

    </div>
    </div>
  );
}

export default RegisterPage;