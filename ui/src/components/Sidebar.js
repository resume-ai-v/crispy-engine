import { FaSuitcase, FaRobot, FaFileAlt, FaCog, FaQuestionCircle } from "react-icons/fa";
import { FiFileText } from "react-icons/fi";  // <-- Add this import!
import { NavLink } from "react-router-dom";

// Optional: To avoid error with linkClasses, define it or remove custom classes for cover letter link.
const linkClasses = (isActive) =>
  `flex items-center gap-3 ${isActive ? "text-purple-600 font-semibold" : "text-gray-700"}`;

export default function Sidebar({ active }) {
  return (
    <div className="w-64 h-screen bg-white shadow-lg p-6 flex flex-col justify-between">
      {/* Top Brand and Navigation */}
      <div>
        <h1 className="text-2xl font-bold text-purple-600 mb-6">
          Launch<span className="text-black">Hire</span>
        </h1>

        <nav className="space-y-4">
          <NavLink
            to="/recommended-jobs"
            className={`flex items-center gap-3 ${
              active === "recommended-jobs"
                ? "text-purple-600 font-semibold"
                : "text-gray-700"
            }`}
          >
            <FaSuitcase /> Recommended Jobs
          </NavLink>

          <NavLink
            to="/ai-interview-practice"
            className={`flex items-center gap-3 ${
              active === "interview"
                ? "text-purple-600 font-semibold"
                : "text-gray-700"
            }`}
          >
            <FaRobot /> AI Interview Practice
          </NavLink>

          {/* Cover Letter Link (Feather Icon) */}
          <NavLink to="/cover-letter-generator" className={({ isActive }) => linkClasses(isActive)}>
            <FiFileText className="mr-3" /> Cover Letter
          </NavLink>

          <NavLink
            to="/ai-resume"
            className={`flex items-center gap-3 ${
              active === "resume"
                ? "text-purple-600 font-semibold"
                : "text-gray-700"
            }`}
          >
            <FaFileAlt /> AI Resume
          </NavLink>
        </nav>
      </div>

      {/* Bottom Settings + Help */}
      <div className="space-y-4 text-gray-700 text-sm pt-4 border-t mt-6">
        <NavLink to="/profile" className="flex items-center gap-2 hover:text-purple-600">
          <FaCog /> Settings
        </NavLink>
        <NavLink to="/help" className="flex items-center gap-2 hover:text-purple-600">
          <FaQuestionCircle /> Help
        </NavLink>
      </div>
    </div>
  );
}
