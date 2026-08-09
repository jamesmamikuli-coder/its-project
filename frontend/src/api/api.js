import axios from "axios";

const BASE_URL = 
import.meta.env.VITE_API_URL;
console.log("BASE URL:", BASE_URL);
const api = axios.create({
  baseURL: BASE_URL,
});


// ==================================================
// CHATBOT API
// ==================================================
export const qaAPI = {
  askQuestion: (message) =>
    api.post("/api/chat", { message }),

  getHistory: () =>
    api.get("/api/history"),
};


// ==================================================
// ARTICLES API
// ==================================================
export const articleAPI = {
  getArticles: () =>
    api.get("/api/articles"),
};


// ==================================================
// ANALYTICS API (SEPARATE - DO NOT MIX)
// ==================================================
export const analyticsAPI = {
  getAnalytics: () =>
    api.get("/api/analytics"),
};
export const authAPI = {

  register: (userData) =>
    api.post("/api/register", userData),

  login: (userData) =>
    api.post("/api/login", userData),

  resetPassword: (data) =>
    api.post("/api/reset-password", data),

};
export const quizAPI = {

    getQuizzes: (topic) =>
        api.get(`/api/quizzes/${topic}`),

    saveScore: (data) =>
        api.post("/api/save-score", data)

};

export const aiQuizAPI = {

  generateQuiz: (topic) =>
    api.post("/api/generate-quiz", {
      topic,
    }),
};
export const dashboardAPI = {

  getDashboard: (username) =>
    api.get(`/api/student-dashboard?username=${username}`)
};
export const leaderboardAPI = {

  getLeaderboard: () =>
    api.get("/api/leaderboard"),
};
export const recommendationAPI = {

  getRecommendations: (username) =>
    api.get(`/api/recommendations?username=${username}`),
};
export const reportAPI = {

  generateReport: () =>
    api.get("/api/generate-report", {
      responseType: "blob",
    }),
};
export const certificateAPI = {

  downloadCertificate: (username) =>
    api.get(
      `/api/certificate/${username}`,
      {
        responseType: "blob"
      }
    )
};
export const topicMasteryAPI = {
   getTopicMastery: (username) =>
    api.get(`/api/topic-mastery/${username}`),
  };
  export default api;