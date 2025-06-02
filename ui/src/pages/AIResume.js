// src/pages/AIResume.js

import React, { useState, useEffect } from "react";
import ResumeCard from "../components/ResumeCard";
import { tailorResume, downloadPDF, downloadDOCX } from "../utils/api";
import { FaDownload } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

export default function AIResume() {
  const [resumeInput, setResumeInput] = useState(() => localStorage.getItem("resumeText") || "");
  const [jobDescription, setJobDescription] = useState("");
  const [tailoredResume, setTailoredResume] = useState("");
  const [originalMatch, setOriginalMatch] = useState(null);
  const [tailoredMatch, setTailoredMatch] = useState(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  // Keep resume input synced to localStorage for use by ResumeEditor
  useEffect(() => {
    localStorage.setItem("resumeText", resumeInput);
  }, [resumeInput]);

  // Handle AI tailoring
  const handleTailor = async () => {
    if (!resumeInput.trim() || !jobDescription.trim()) {
      alert("Please provide both your resume text and a job description.");
      return;
    }
    setLoading(true);
    try {
      const res = await tailorResume(resumeInput, jobDescription, "Generic", "Unknown");
      setTailoredResume(res.tailored_resume);
      setOriginalMatch(res.original_match);
      setTailoredMatch(res.tailored_match);
      localStorage.setItem("tailoredResumeText", res.tailored_resume || "");
    } catch (err) {
      alert("❌ Failed to tailor resume with AI. Please try again.");
    }
    setLoading(false);
  };

  // Handle PDF/DOCX download
  const handleDownload = async (format) => {
    const textToDownload = tailoredResume || resumeInput;
    if (!textToDownload) {
      alert("Nothing to download. Please tailor your resume first or enter resume text.");
      return;
    }
    try {
      if (format === "pdf") {
        await downloadPDF(textToDownload, "AI_Resume");
      } else if (format === "docx") {
        await downloadDOCX(textToDownload, "AI_Resume");
      }
    } catch (err) {
      alert("❌ Download failed. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <main className="flex flex-1 w-full max-w-7xl mx-auto gap-8 py-12 px-4">
        {/* LEFT: Tailoring Form */}
        <section className="w-full max-w-lg bg-white rounded-2xl shadow p-8 flex flex-col justify-start">
          <h1 className="text-3xl font-bold mb-6 text-gray-900">AI-Powered Resume Tailoring</h1>
          <div className="mb-5">
            <label className="block font-semibold mb-1">Your Resume (Plain Text):</label>
            <textarea
              className="w-full p-3 border border-gray-200 rounded-lg h-32 focus:outline-none focus:ring focus:border-purple-400"
              value={resumeInput}
              onChange={(e) => setResumeInput(e.target.value)}
              placeholder="Paste your current resume text here..."
            />
          </div>
          <div className="mb-5">
            <label className="block font-semibold mb-1">Job Description (Plain Text):</label>
            <textarea
              className="w-full p-3 border border-gray-200 rounded-lg h-32 focus:outline-none focus:ring focus:border-purple-400"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here..."
            />
          </div>
          <button
            onClick={handleTailor}
            disabled={loading}
            className="bg-purple-600 text-white px-6 py-3 rounded-xl hover:bg-purple-700 transition mb-4 w-full font-semibold"
          >
            {loading ? "Tailoring…" : "Tailor My Resume with AI"}
          </button>
          {(originalMatch !== null && tailoredMatch !== null) && (
            <div className="mb-1 text-gray-700 flex gap-4 items-center justify-between px-1">
              <span>
                <span className="font-semibold">Original Match:</span> {originalMatch}
              </span>
              <span>
                <span className="font-semibold">Tailored Match:</span> {tailoredMatch}
              </span>
            </div>
          )}
        </section>

        {/* RIGHT: Resume Card Preview */}
        <section className="flex-1 max-w-2xl flex flex-col items-center bg-white rounded-2xl shadow p-10">
          <div className="flex justify-between w-full mb-3">
            <h2 className="text-xl font-bold">AI Resumes</h2>
            <div className="flex gap-2">
              <button
                onClick={() => handleDownload("pdf")}
                className="flex items-center gap-2 text-purple-700 px-3 py-1 border border-purple-200 rounded hover:bg-purple-50 transition"
              >
                <FaDownload /> PDF
              </button>
              <button
                onClick={() => handleDownload("docx")}
                className="flex items-center gap-2 text-purple-700 px-3 py-1 border border-purple-200 rounded hover:bg-purple-50 transition"
              >
                <FaDownload /> DOCX
              </button>
              {/* Resume Editor Button */}
              <button
                className="bg-purple-100 text-purple-700 px-4 py-1 rounded ml-2 hover:bg-purple-200"
                onClick={() => navigate("/resume-editor")}
              >
                ✏️ Open Resume Editor
              </button>
            </div>
          </div>
          <ResumeCard resumeText={tailoredResume || resumeInput} />
        </section>
      </main>
    </div>
  );
}
