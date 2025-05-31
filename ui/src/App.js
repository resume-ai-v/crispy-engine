import React from "react";
import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Onboarding from "./pages/Onboarding";
import RecommendedJobs from "./pages/RecommendedJobs";
import JobDetail from "./pages/JobDetail";
import AIResume from "./pages/AIResume";
import AIInterviewPractice from "./pages/AIInterviewPractice";
import Sidebar from "./components/Sidebar";
import InlineEditor from "./pages/InlineEditor";



function LayoutWithSidebar({ children, active }) {
  return (
    <div className="flex">
      <Sidebar active={active} />
      <div className="flex-1">{children}</div>
    </div>
  );
}

function AppRoutes() {
  const location = useLocation();
  const noSidebarPaths = ["/", "/signup", "/onboarding"];
  const isNoSidebar = noSidebarPaths.includes(location.pathname);

  return (
    <>
      {isNoSidebar ? (
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/inline-editor" element={<InlineEditor />} />

        </Routes>
      ) : (
        <Routes>
          <Route
            path="/recommended-jobs"
            element={
              <LayoutWithSidebar active="recommended-jobs">
                <RecommendedJobs />
              </LayoutWithSidebar>
            }
          />
          <Route
            path="/job/:id"
            element={
              <LayoutWithSidebar active="recommended-jobs">
                <JobDetail />
              </LayoutWithSidebar>
            }
          />
          <Route
            path="/ai-resume"
            element={
              <LayoutWithSidebar active="resume">
                <AIResume />
              </LayoutWithSidebar>
            }
          />
          <Route
            path="/ai-interview-practice"
            element={
              <LayoutWithSidebar active="interview">
                <AIInterviewPractice />
              </LayoutWithSidebar>
            }
          />
        </Routes>
      )}
    </>
  );
}

export default function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}
