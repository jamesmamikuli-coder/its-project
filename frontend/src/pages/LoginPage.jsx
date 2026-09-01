import { useState } from "react";

import { authAPI } from "../api/api";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";

function LoginPage() {

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
const [showPassword, setShowPassword] = useState(false);
const navigate = useNavigate();

  const handleLogin = async () => {
if (!email.trim()) {
    toast.error("Email is required");
    return;
}

if (!password.trim()) {
    toast.error("Password is required");
    return;
}

    try {
        setLoading(true);

      const res = await authAPI.login({
        email,
        password,
      });

      console.log(res.data);

      // ==========================================
      // LOGIN SUCCESS
      // ==========================================
      if (res.data.message === "Login successful") {

        // SAVE USERNAME
        localStorage.setItem(
          "username",
          res.data.user.username
        );
         localStorage.setItem(
          "role",
          res.data.user.role
         );

       toast.success("Welcome back " + res.data.user.username + " 🎉");

setTimeout(() => {

    if (res.data.user.role === "admin") {

        navigate("/admin-dashboard");

    } else {

        navigate("/dashboard");

    }

}, 1000);
      } else {

        toast.error("Invalid email or password");
      }

    } catch (err) {
      
          setLoading(false);
      

      console.log(err);

     toast.error("Unable to login");
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
        fontSize: "24px",
        lineHeight: "1.3",
        margin: "0 auto 15px auto",
        fontWeight: "600",
        maxWidth: "430px"
       
    }}
>
🎓 Intelligent Tutoring  System for Automated Question Answering and Student Performance Analytics
</h1>

<p
    style={{
        textAlign: "center",
        color: "#666",
        marginBottom: "35px"
    }}
>
Welcome Back! Login to continue learning.
</p>

      <div style={{ marginBottom: "10px" }}>

        <input
    type="email"
    placeholder="📧 Enter Email"
    value={email}
    onChange={(e) => setEmail(e.target.value)}
    style={{
        width: "100%",
        padding: "15px",
        marginBottom: "18px",
        borderRadius: "12px",
        border: "2px solid #E5E7EB",
        fontSize: "16px",
        outline: "none",
        boxSizing: "border-box"
    }}
/>
      </div>

      <div style={{ marginBottom: "10px" }}>

       <div
    style={{
        position: "relative",
        marginBottom: "25px"
    }}
>

<input
    type={showPassword ? "text" : "password"}
    placeholder="🔒 Enter Password"
    value={password}
    onChange={(e) => setPassword(e.target.value)}
    style={{
        width: "100%",
        padding: "15px",
        borderRadius: "12px",
        border: "2px solid #E5E7EB",
        fontSize: "16px",
        outline: "none",
        boxSizing: "border-box"
    }}
/>

<Link
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
</Link>

</div>
      </div>
      <div
    style={{
        textAlign: "right",
        marginBottom: "20px"
    }}
>

<Link
    to="/forgot-password"
    style={{
        color: "#2563EB",
        textDecoration: "none",
        fontWeight: "600",
        fontSize: "14px"
    }}
>
    Forgot Password?
</Link>

</div>

     <button
    onClick={handleLogin}
    onMouseEnter={(e)=>{
    e.target.style.transform="translateY(-2px)";
}}

onMouseLeave={(e)=>{
    e.target.style.transform="translateY(0)";
}}
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
        boxShadow: "0 8px 20px rgba(37,99,235,.35)",
        transition: ".3s"
    }}
>
   {loading ? "⏳ Logging in..." : "🚀 Login"}
</button>
<div
style={{
textAlign:"center",
marginTop:"20px",
fontSize:"15px"
}}
>

<p>
Don't have an account?

<Link
to="/register"
style={{
color:"#2563EB",
fontWeight:"bold",
cursor:"pointer",
marginLeft:"5px"
}}
>
Register
</Link>

</p>

</div>

    </div>
    </div>
    
  );
}

export default LoginPage;