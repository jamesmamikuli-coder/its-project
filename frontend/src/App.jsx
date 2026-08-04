import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Layout from "./components/Layout";
import { Toaster } from "react-hot-toast";

import DashboardPage from "./pages/DashboardPage.jsx";
import ChatbotPage from "./pages/ChatbotPage.jsx";
import AnalyticsPage from "./pages/AnalyticsPage.jsx";
import KnowledgePage from "./pages/KnowledgePage.jsx";
import QuizPage from "./pages/QuizPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";
import AIQuizGeneratorPage from "./pages/AIQuizGeneratorPage.jsx";
import LeaderboardPage from "./pages/LeaderboardPage.jsx";
import RecommendationPage from "./pages/RecommendationPage.jsx";
import AdminPage from "./pages/AdminPage.jsx";
import AdvancedAnalyticsPage from "./pages/AdvancedAnalyticsPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import StudentManagementPage from "./pages/StudentManagementPage.jsx";
import StudentPerformancePage from "./pages/StudentPerformancePage.jsx";
import AdminDashboard from "./pages/AdminDashboard.jsx";
import ForgotPasswordPage from "./pages/ForgotPasswordPage.jsx";
export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
      <Toaster
    position="top-right"
    toastOptions={{
        duration: 3000,
        style: {
            borderRadius: "12px",
            background: "#fff",
            color: "#333"
        }
    }}
/>

        <Routes>
          {/* Layout wrapper */}
          <Route element={<Layout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/chatbot" element={<ChatbotPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/knowledge" element={<KnowledgePage />} />
          </Route>
            <Route path="/quiz" element={<QuizPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/ai-quiz" element={<AIQuizGeneratorPage />} />
               <Route path="/leaderboard" element={<LeaderboardPage />} />
                <Route path="/recommendations" element={<RecommendationPage />} />
                <Route path="/admin" element={<AdminPage />} />
                  <Route path="/advanced-analytics" element={<AdvancedAnalyticsPage />} />
                  <Route path="/profile" element={<ProfilePage />} />
                  <Route path="/students" element={<StudentManagementPage />} />
                  <Route path="/student-performance/:username" element={<StudentPerformancePage />} />
                   <Route path="/admin-dashboard" element={<AdminDashboard />} />
                   <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        </Routes>

      </BrowserRouter>
    </AuthProvider>
  );
}