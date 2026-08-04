import { useEffect, useState } from "react";

import {
  recommendationAPI
} from "../api/api";

function RecommendationPage() {

  const [recommendations,
    setRecommendations] = useState([]);

  useEffect(() => {

    recommendationAPI
      .getRecommendations()

      .then((res) => {

        setRecommendations(
          res.data.recommendations
        );

      })

      .catch((err) => {

        console.log(err);
      });

  }, []);

  return (

    <div style={{ padding: "20px" }}>

      <h1>
        🧠 Adaptive Learning Recommendations
      </h1>

      {
        recommendations.length === 0 ? (

          <p>No recommendations yet</p>

        ) : (

          recommendations.map((rec, index) => (

            <div
              key={index}
              style={{
                border: "1px solid #ccc",
                padding: "15px",
                marginBottom: "15px",
                borderRadius: "10px",
              }}
            >

              <h2>
                Weak Topic: {rec.topic}
                </h2>

              <p>
                {rec.recommendation}
                </p>

            </div>
          ))
        )
      }

    </div>
  );
}

export default RecommendationPage;