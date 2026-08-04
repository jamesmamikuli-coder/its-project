import axios from "axios";

const BASE_URL = "http://localhost:5000";

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
    axios.get(
      `http://127.0.0.1:5000/api/certificate/${username}`,
      {
        responseType: "blob"
      }
    )
};
export const getTopicMastery = (username) =>
    axios.get(`${API_URL}/topic-mastery/${username}`);