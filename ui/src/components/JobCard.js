// src/components/JobCard.js

import React, { useState } from "react";
import { FaMapMarkerAlt, FaBriefcase, FaClock } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

function getMatchLabel(score) {
  if (score >= 95) return "Perfect Match";
  if (score >= 85) return "90% Match";
  if (score >= 70) return "Good Match";
  return "Potential";
}

function getMatchColor(score) {
  if (score >= 95) return "bg-black";
  if (score >= 85) return "bg-purple-800";
  if (score >= 70) return "bg-gray-700";
  return "bg-gray-400";
}

export default function JobCard({ job }) {
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  // User’s resume (text) should have been saved to localStorage during onboarding
  const resume = localStorage.getItem("resumeText") || "";

  // When user chooses “Tailor Resume with AI”
  const handleTailorClick = () => {
    setShowModal(false);
    navigate(`/apply/${job.id}`);
  };

  // When user chooses “Use My Current Resume”
  const handleUseCurrentClick = () => {
    setShowModal(false);
    navigate(`/apply/${job.id}`);
  };

  return (
    <>
      {/* ---- Job Card UI ---- */}
      <div className="bg-white rounded-2xl shadow border border-gray-100 p-6 flex flex-col min-h-[340px] transition hover:shadow-xl">
        {/* Header: Logo + Title/Company */}
        <div className="flex items-center mb-3">
          <img
            src={job.logo || "https://cdn-icons-png.flaticon.com/512/174/174872.png"}
            alt={job.company || "Company"}
            className="h-12 w-12 rounded-xl object-contain bg-gray-100 mr-3"
          />
          <div>
            <h2 className="text-lg font-semibold">{job.title}</h2>
            <div className="text-gray-500 text-sm">{job.company}</div>
          </div>
        </div>

        {/* Info Row: Location, Type, Entry-Level, Posted */}
        <div className="flex flex-wrap gap-2 text-gray-600 text-sm mb-3">
          <div className="flex items-center gap-1">
            <FaMapMarkerAlt className="mr-1" /> {job.location}
          </div>
          <div className="flex items-center gap-1">
            <FaBriefcase className="mr-1" /> {job.type}
          </div>
          <div className="flex items-center gap-1">
            <span className="mr-1">⭐</span> Entry-Level
          </div>
          <div className="flex items-center gap-1">
            <FaClock className="mr-1" /> {job.posted || "1hr ago"}
          </div>
        </div>

        {/* Salary + Match Badge */}
        <div className="flex items-center mb-3">
          <span className="font-semibold text-gray-900 mr-3">
            {job.salary || "$120k / yr - $150k / yr"}
          </span>
          <span
            className={`ml-auto px-3 py-1 rounded-xl text-white font-bold text-xs ${getMatchColor(
              job.numeric_score
            )}`}
          >
            {getMatchLabel(job.numeric_score)}
          </span>
        </div>

        {/* “Less than 10 applicants” + Apply Now Button */}
        <div className="text-xs text-gray-500 mb-3">Less than 10 applicants</div>
        <button
          className="bg-purple-500 hover:bg-purple-700 text-white font-semibold rounded-xl px-4 py-2 mt-auto transition"
          onClick={() => setShowModal(true)}
        >
          Apply Now
        </button>
      </div>

      {/* ---- Modal (two choice buttons) ---- */}
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/30 z-40">
          <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-sm relative">
            <button
              onClick={() => setShowModal(false)}
              className="absolute right-4 top-4 text-xl"
            >
              ✕
            </button>
            <h3 className="text-xl font-semibold mb-4">How do you want to apply?</h3>
            <div className="flex flex-col space-y-4">
              <button
                onClick={handleTailorClick}
                className="bg-purple-600 text-white rounded-lg px-4 py-2 text-center hover:bg-purple-700 transition"
              >
                Tailor Resume with AI
              </button>
              <button
                onClick={handleUseCurrentClick}
                className="border border-gray-300 rounded-lg px-4 py-2 text-center hover:bg-gray-100 transition"
              >
                Use My Current Resume
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
