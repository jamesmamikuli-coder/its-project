import { useState } from "react";
import { authAPI } from "../api/api";
import toast from "react-hot-toast";

function ForgotPasswordPage() {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleReset = async () => {
        if (!email || !password) {
    toast.error("Please fill in all fields.");
    return;
}

        try {

            const res = await authAPI.resetPassword({
                email,
                password
            });

            toast.success(res.data.message);

        } catch (err) {

            toast.error("Password reset failed");

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
                background: "linear-gradient(135deg,#2563EB,#1E3A8A)"
            }}
        >

            <div
                style={{
                    background: "#fff",
                    padding: "40px",
                    width: "420px",
                    borderRadius: "20px",
                    boxShadow: "0 15px 35px rgba(0,0,0,.2)"
                }}
            >

                <h2 style={{textAlign:"center"}}>
                    🔑 Reset Password
                </h2>

                <br/>

                <input
                    type="email"
                    placeholder="Enter Email"
                    value={email}
                    onChange={(e)=>setEmail(e.target.value)}
                    style={{
                        width:"100%",
                        padding:"15px",
                        marginBottom:"20px"
                    }}
                />

                <input
                    type="password"
                    placeholder="New Password"
                    value={password}
                    onChange={(e)=>setPassword(e.target.value)}
                    style={{
                        width:"100%",
                        padding:"15px"
                    }}
                />

                <br/><br/>

                <button
                    onClick={handleReset}
                    style={{
                        width:"100%",
                        padding:"15px",
                        background:"#2563EB",
                        color:"#fff",
                        border:"none",
                        borderRadius:"12px",
                        fontSize:"18px"
                    }}
                >

                    Reset Password

                </button>

            </div>

        </div>

    );

}

export default ForgotPasswordPage;
