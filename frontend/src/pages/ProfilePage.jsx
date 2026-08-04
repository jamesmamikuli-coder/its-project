import { useEffect, useState } from "react";
import axios from "axios";

function ProfilePage() {

  const [profile, setProfile] = useState(null);

  const [achievements, setAchievements] = useState([]);
  const downloadCertificate = async () => {

  const username =
    localStorage.getItem("username");

  const response =
    await fetch(
      `http://127.0.0.1:5000/api/certificate/${username}`
    );

  const blob =
    await response.blob();

  const url =
    window.URL.createObjectURL(blob);

  const link =
    document.createElement("a");

  link.href = url;

  link.download =
    `${username}_certificate.pdf`;

  link.click();
};

  useEffect(() => {

    const username =
      localStorage.getItem("username");

    // ==========================================
    // LOAD PROFILE
    // ==========================================
    axios
      .get(
        `http://127.0.0.1:5000/api/student-profile/${username}`
      )
      .then((res) => {

        setProfile(res.data);

      })
      .catch((err) => {

        console.log(err);

      });

    // ==========================================
    // LOAD ACHIEVEMENTS
    // ==========================================
    axios
      .get(
        `http://127.0.0.1:5000/api/achievements/${username}`
      )
      .then((res) => {

        setAchievements(
          res.data.achievements
        );

      })
      .catch((err) => {

        console.log(err);

      });

  }, []);

  if (!profile) {

    return <h2>Loading profile...</h2>;
  }

  return (

    <div style={{ padding: "20px" }}>

      <h1>👤 Student Profile</h1>

      <p>
        <strong>Username:</strong>{" "}
        {profile.username}
      </p>

      <p>
        <strong>Email:</strong>{" "}
        {profile.email}
      </p>

      <p>
        <strong>Role:</strong>{" "}
        {profile.role}
      </p>

      <hr />

      <h2>📊 Performance Statistics</h2>

      <p>
        Total Quizzes: {profile.total_quizzes}
      </p>

      <p>
        Average Score: {profile.average_score}
      </p>

      <p>
        Highest Score: {profile.highest_score}
      </p>

      <hr />

      <h2>🏆 Achievements</h2>
      <button
  onClick={downloadCertificate}
>
  🎓 Download Certificate
</button>

      {
        achievements.length === 0
        ? (
            <p>
              No achievements yet
            </p>
          )
        : (
            achievements.map((badge, index) => (

              <div key={index}>

                <p>
                  {
  badge.badge === "Gold Scholar"
    ? "🥇 Gold Scholar"

  : badge.badge === "Silver Scholar"
    ? "🥈 Silver Scholar"

  : badge.badge === "Bronze Scholar"
    ? "🥉 Bronze Scholar"

  : badge.badge === "Quiz Master"
    ? "🏆 Quiz Master"

  : badge.badge === "Consistent Learner"
    ? "🔥 Consistent Learner"

  : `🏅 ${badge.badge}`
}
                </p>

              </div>

            ))
          )
      }

    </div>

  );
}

export default ProfilePage;