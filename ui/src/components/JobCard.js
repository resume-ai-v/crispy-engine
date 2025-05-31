import React from "react";
import { useNavigate } from "react-router-dom";
import {
  FaMapMarkerAlt,
  FaBriefcase,
  FaMoneyBillWave,
  FaClock,
  FaUserFriends,
} from "react-icons/fa";
import { timeAgo } from "../utils/timeAgo";

export default function JobCard({ job }) {
  const navigate = useNavigate();
  const handleClick = () => navigate(`/job/${job.id}`);

  const scoreMatch = job?.match_score?.match(/\d+%/)?.[0] || "";
  const matchLabel =
    parseInt(scoreMatch) >= 95
      ? "Perfect Match"
      : parseInt(scoreMatch) >= 80
      ? `${scoreMatch} Match`
      : "";

  return (
    <div className="bg-white rounded-lg shadow-md p-5">
      {/* Header: logo + title */}
      <div className="flex items-center mb-3">
        <img
          src={job.logo || "/default-logo.png"}
          alt={job.company}
          className="w-10 h-10 rounded mr-4 object-contain"
        />
        <div>
          <h2 className="text-md font-semibold text-gray-900">
            {job.title}
          </h2>
          <p className="text-sm text-gray-500">{job.company}</p>
        </div>
      </div>

      {/* Job Info */}
      <div className="text-sm text-gray-600 space-y-1 mb-4">
        <div className="flex items-center gap-2">
          <FaMapMarkerAlt className="text-gray-500" />
          {job.location || "Remote"}
        </div>
        <div className="flex items-center gap-2">
          <FaBriefcase className="text-gray-500" />
          {job.type || "Full Time"}
        </div>
        <div className="flex items-center gap-2">
          <FaMoneyBillWave className="text-gray-500" />
          {job.salary || "Not specified"}
        </div>
        <div className="flex items-center gap-2">
          <FaClock className="text-gray-500" />
          {job.posted ? timeAgo(job.posted) : "Recently"}
        </div>
      </div>

      {/* ✅ Match + Applicants */}
      <div className="flex items-center justify-between mb-3">
        {matchLabel && (
          <span className="px-2 py-1 text-xs rounded bg-black text-white">
            {matchLabel}
          </span>
        )}
        <span className="text-xs text-gray-600 flex items-center gap-1">
          <FaUserFriends /> {job.applicants || "Less than 10 applicants"}
        </span>
      </div>

      <button
        onClick={handleClick}
        className="w-full bg-purple-600 text-white font-semibold py-2 rounded hover:bg-purple-700"
      >
        Apply Now
      </button>
    </div>
  );
}
