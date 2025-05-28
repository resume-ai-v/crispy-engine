import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Onboarding from './pages/Onboarding';
import RecommendedJobs from './pages/RecommendedJobs';
import AIInterviewPractice from './pages/AIInterviewPractice';
import AIResume from './pages/AIResume';
import Settings from './pages/Settings';
import Help from './pages/Help';
import Profile from './pages/Profile';
import EditProfile from './pages/EditProfile';
import JobDetailView from "./pages/JobDetailView";



function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/onboarding" element={<Onboarding />} />
        <Route path="/recommended-jobs" element={<RecommendedJobs />} />
        <Route path="/ai-interview-practice" element={<AIInterviewPractice />} />
        <Route path="/ai-resume" element={<AIResume />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/help" element={<Help />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/edit-profile" element={<EditProfile />} />
        <Route path="/job/:id" element={<JobDetailView />} />
      </Routes>
    </Router>
  );
}

export default App;
