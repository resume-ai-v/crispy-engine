// src/pages/JobDetail.js

import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getJobDetail, tailorResume } from "../utils/api";

export default function JobDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tailoring, setTailoring] = useState(false);

  // Retrieve the user’s stored resume from localStorage (set during onboarding)
  const resume = localStorage.getItem("resumeText") || "";

  // Fetch job details (including match score) on mount
  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const result = await getJobDetail(id, resume);
        // Backend returns: { job: { …, match_score, explanation, jd_text, url, … } }
        setJob(result.job);
        // Optionally store JD and URL for further pages
        localStorage.setItem("selectedJobJD", result.job.jd_text || "");
        localStorage.setItem("selectedJobURL", result.job.url || "");
        localStorage.setItem("matchScore", result.job.match_score || "");
      } catch (err) {
        console.error("Error fetching job details:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [id, resume]);

  // When user clicks “Tailor Resume” button
  const handleTailorResume = async () => {
    if (!job) return;

    setTailoring(true);
    try {
      // tailorResume returns: { tailored_resume, original_match, tailored_match }
      const tailored = await tailorResume(resume, job.jd_text, job.title, job.company);
      localStorage.setItem("tailoredResume", tailored.tailored_resume || "");
      localStorage.setItem("originalMatch", tailored.original_match || "0");
      localStorage.setItem("tailoredMatch", tailored.tailored_match || "0");
      // Redirect to an inline editor or another page where user can refine further
      navigate("/inline-editor");
    } catch (err) {
      console.error("Tailoring failed:", err);
      alert("❌ Failed to tailor resume. Please try again.");
    }
    setTailoring(false);
  };

  if (loading) return <div className="p-8">Loading job details…</div>;
  if (!job) return <div className="p-8">Job not found.</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-2">{job.title}</h2>
      <p className="text-gray-600 mb-1">{job.company}</p>
      <p className="text-sm text-gray-500 mb-2">{job.location}</p>

      {/* Display match score */}
      {job.match_score !== undefined && (
        <div className="inline-block bg-black text-white text-sm px-3 py-1 rounded mb-3">
          {job.match_score}% Match
        </div>
      )}

      {/* Job Description */}
      <p className="text-md text-gray-800 leading-relaxed whitespace-pre-wrap mb-4">
        {job.jd_text}
      </p>

      {/* Step 1: Ask if user wants to tailor or use original */}
      <div className="mt-6">
        <p className="font-medium mb-2">
          Would you like to tailor your resume for this job?
        </p>
        <button
          onClick={() => setTailoring(true) || handleTailorResume()}
          disabled={tailoring}
          className={`${
            tailoring
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-purple-600 hover:bg-purple-700"
          } text-white px-4 py-2 rounded-lg mr-4`}
        >
          {tailoring ? "Tailoring…" : "Yes, Tailor It"}
        </button>
        <button
          onClick={() => window.open(job.url, "_blank")}
          className="border px-4 py-2 rounded-lg hover:bg-gray-100 transition"
        >
          No, Apply with Original
        </button>
      </div>
    </div>
  );
}
