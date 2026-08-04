import React from "react";

export default function LoadingSpinner({
  message = "Loading...",
}) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        background: "#F4F7FB",
      }}
    >
      <div
        style={{
          width: "70px",
          height: "70px",
          border: "7px solid #E5E7EB",
          borderTop: "7px solid #2563EB",
          borderRadius: "50%",
          animation: "spin 1s linear infinite",
        }}
      />

      <h2
        style={{
          marginTop: "25px",
          color: "#1E3A8A",
        }}
      >
        {message}
      </h2>

      <p
        style={{
          color: "#777",
        }}
      >
        Please wait...
      </p>
    </div>
  );
}