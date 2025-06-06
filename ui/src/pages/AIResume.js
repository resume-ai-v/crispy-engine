// src/pages/AIResume.js

import React, { useState, useEffect } from "react";
import ResumeCard from "../components/ResumeCard";
import { uploadResume, tailorResume, downloadPDF, downloadDOCX } from "../utils/api";
import { FaDownload } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

export default function AIResume() {
  const [resumeText, setResumeText] = useState(() => localStorage.getItem("resumeText") || "");
  const [uploading, setUploading] = useState(false);
  const [jobDescription, setJobDescription] = useState("");
  const [tailoredResume, setTailoredResume] = useState("");
  const [originalMatch, setOriginalMatch] = useState(null);
  const [tailoredMatch, setTailoredMatch] = useState(null);
  const [atsScore, setATSScore] = useState(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  // Keep resume in localStorage for editing/viewing continuity
  useEffect(() => {
    localStorage.setItem("resumeText", resumeText);
  }, [resumeText]);

  // Handle resume file upload (PDF/DOCX/TXT)
  const handleResumeUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      const res = await uploadResume(file);
      setResumeText(res.resume_text || "");
      localStorage.setItem("resumeText", res.resume_text || "");
      setTailoredResume("");
      setOriginalMatch(null);
      setTailoredMatch(null);
      setATSScore(null);
      alert("✅ Resume uploaded and parsed successfully!");
    } catch (err) {
      alert("❌ Failed to upload/parse resume.");
    }
    setUploading(false);
  };

  // Tailor resume with AI
  const handleTailor = async () => {
    if (!resumeText.trim() || !jobDescription.trim()) {
      alert("Please provide both your resume and a job description.");
      return;
    }
    setLoading(true);
    try {
      const res = await tailorResume(resumeText, jobDescription, "Generic", "Unknown");
      setTailoredResume(res.tailored_resume);
      setOriginalMatch(res.original_match);
      setTailoredMatch(res.tailored_match);
      setATSScore(res.ats_score ?? null);
      localStorage.setItem("tailoredResumeText", res.tailored_resume || "");
    } catch (err) {
      alert("❌ Failed to tailor resume with AI. Please try again.");
    }
    setLoading(false);
  };

  // Download PDF/DOCX
  const handleDownload = async (format) => {
    const textToDownload = tailoredResume || resumeText;
    if (!textToDownload) {
      alert("Nothing to download. Please upload or tailor your resume first.");
      return;
    }
    try {
      let blob;
      if (format === "pdf") blob = await downloadPDF(textToDownload);
      else blob = await downloadDOCX(textToDownload);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `AI_Resume.${format}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("❌ Download failed. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <main className="flex flex-1 w-full max-w-7xl mx-auto gap-8 py-12 px-4">
        {/* LEFT: Resume upload + tailoring */}
        <section className="w-full max-w-lg bg-white rounded-2xl shadow p-8 flex flex-col justify-start">
          <h1 className="text-3xl font-bold mb-6 text-gray-900">AI-Powered Resume Tailoring</h1>
          <div className="mb-5">
            <label className="block font-semibold mb-1">Your Resume (PDF/DOCX/Text):</label>
            <div className="flex gap-2 mb-2">
              <input
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleResumeUpload}
                className="block"
                disabled={uploading}
              />
              {uploading && <span className="text-xs text-purple-700">Uploading…</span>}
              {resumeText && (
                <button
                  className="ml-auto text-sm bg-purple-100 px-2 py-1 rounded"
                  onClick={() => setResumeText("")}
                  type="button"
                >
                  Clear
                </button>
              )}
            </div>
            {/* Only show textarea if no resume uploaded */}
            {!resumeText && (
              <textarea
                className="w-full p-3 border border-gray-200 rounded-lg h-32 focus:outline-none focus:ring focus:border-purple-400"
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste your current resume text here..."
              />
            )}
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
          {(originalMatch !== null || tailoredMatch !== null) && (
            <div className="mb-1 flex flex-col gap-2 items-start justify-between px-1">
              {originalMatch !== null && (
                <span className="font-semibold text-gray-700">
                  Original Match: <span className="text-black">{originalMatch}%</span>
                </span>
              )}
              {tailoredMatch !== null && (
                <span className="font-semibold text-green-700">
                  Tailored Match: <span className="text-black">{tailoredMatch}%</span>
                </span>
              )}
              {atsScore !== null && (
                <span className="font-semibold text-blue-700">
                  ATS Score: <span className="text-black">{atsScore}%</span>
                </span>
              )}
            </div>
          )}
        </section>

        {/* RIGHT: Resume Preview/Editor */}
        <section className="flex-1 max-w-2xl flex flex-col items-center bg-white rounded-2xl shadow p-10">
          <div className="flex justify-between w-full mb-3">
            <h2 className="text-xl font-bold">AI Resume Preview</h2>
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
              <button
                className="bg-purple-100 text-purple-700 px-4 py-1 rounded ml-2 hover:bg-purple-200"
                onClick={() => navigate("/resume-editor")}
              >
                ✏️ Open Resume Editor
              </button>
            </div>
          </div>
          <ResumeCard resumeText={tailoredResume || resumeText} />
        </section>
      </main>
    </div>
  );
}
