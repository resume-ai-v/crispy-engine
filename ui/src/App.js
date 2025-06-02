// src/App.js

import React from "react";
import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Onboarding from "./pages/Onboarding";
import RecommendedJobs from "./pages/RecommendedJobs";
import JobDetail from "./pages/JobDetail";
import AIResume from "./pages/AIResume";
import AIInterviewPractice from "./pages/AIInterviewPractice";
import ApplyPage from "./pages/ApplyPage";
import Sidebar from "./components/Sidebar";
import InlineEditor from "./pages/InlineEditor";
import ResumeEditor from "./components/ResumeEditor"; // FIXED: use pages, not components

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
    <Routes>
      {/* No sidebar pages (Auth & Onboarding) */}
      <Route path="/" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/onboarding" element={<Onboarding />} />

      {/* Sidebar layout pages */}
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
        path="/apply/:id"
        element={
          <LayoutWithSidebar active="recommended-jobs">
            <ApplyPage />
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
      <Route
        path="/inline-editor"
        element={
          <LayoutWithSidebar active="resume">
            <InlineEditor />
          </LayoutWithSidebar>
        }
      />
      <Route
        path="/resume-editor"
        element={
          <LayoutWithSidebar active="resume">
            <ResumeEditor />
          </LayoutWithSidebar>
        }
      />
    </Routes>
  );
}

export default function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}
