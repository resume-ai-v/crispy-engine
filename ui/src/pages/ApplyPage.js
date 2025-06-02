// src/pages/ApplyPage.js

import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { tailorResume, autoApplyJob, downloadPDF, downloadDOCX } from "../utils/api";
import { FaDownload } from "react-icons/fa";
import "./ApplyPage.css"; // Optional: your styling

export default function ApplyPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tailoring, setTailoring] = useState(false);
  const [tailoredResume, setTailoredResume] = useState("");
  const [matchInfo, setMatchInfo] = useState({ original: 0, tailored: 0 });
  const [applying, setApplying] = useState(false);

  // We assume resume text is stored in localStorage under "resumeText"
  const resume = localStorage.getItem("resumeText") || "";

  // 1) Fetch the job details (including initial match score) on mount
  useEffect(() => {
    async function fetchJobDetail() {
      try {
        const res = await fetch(
          `${process.env.REACT_APP_API_BASE || ""}/api/job/${id}`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ resume }), // send the resume so backend can compute original match
          }
        );
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Failed to fetch job detail");
        }
        const data = await res.json();
        setJob(data.job);
        // We expect data.job.match_score to be a number (0–100)
        setMatchInfo((prev) => ({
          ...prev,
          original: data.job.match_score || 0,
        }));
      } catch (err) {
        console.error("Error fetching job:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchJobDetail();
  }, [id, resume]);

  if (loading) {
    return <div className="apppage-container">Loading job details…</div>;
  }
  if (!job) {
    return <div className="apppage-container">Job not found.</div>;
  }

  // 2) Handle “Tailor Resume with AI”
  const handleTailor = async () => {
    setTailoring(true);
    try {
      const res = await tailorResume(resume, job.jd_text, job.title, job.company);
      setTailoredResume(res.tailored_resume || "");
      setMatchInfo({
        original: res.original_match || 0,
        tailored: res.tailored_match || 0,
      });
    } catch (err) {
      console.error("❌ Tailoring failed:", err);
      alert("❌ Something went wrong while tailoring the résumé. Check your API key / token limits / prompt.");
    }
    setTailoring(false);
  };

  // 3) Handle Download (PDF or DOCX)
  const handleDownload = async (format) => {
    try {
      const textToDownload = tailoredResume || resume;
      let blob;
      if (format === "pdf") {
        blob = await downloadPDF(textToDownload, "AI_Resume");
      } else if (format === "docx") {
        blob = await downloadDOCX(textToDownload, "AI_Resume");
      } else {
        throw new Error("Unsupported format");
      }
      // Trigger download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `AI_Resume.${format}`;
      a.click();
      a.remove();
    } catch (err) {
      console.error("❌ Download failed:", err);
      alert("❌ Download failed. Please try again.");
    }
  };

  // 4) Handle Auto-Apply
  const handleAutoApply = async () => {
    setApplying(true);
    try {
      const payload = {
        resume: tailoredResume || resume,
        job_url: job.url,
        job_title: job.title,
        company: job.company,
      };
      const res = await autoApplyJob(payload);
      console.log("Auto-apply result:", res);
      // Open the actual job URL in a new tab
      window.open(job.url, "_blank");
    } catch (err) {
      console.error("❌ Auto-apply failed:", err);
      alert("❌ Auto-apply failed. Please try again.");
    }
    setApplying(false);
  };

  return (
    <div className="apppage-container">
      <button className="back-button" onClick={() => navigate(-1)}>
        ← Back to Jobs
      </button>

      <h1 className="job-title">{job.title}</h1>
      <div className="job-subtitle">
        {job.company} • {job.location}
      </div>
      <div className="job-type">{job.type}</div>

      {/* Match Scores */}
      <div className="match-scores-container">
        <div className="score-box">
          <span className="score-label">Original Match:</span>
          <span className="score-value">{matchInfo.original}%</span>
        </div>
        <div className="score-box">
          <span className="score-label">After Tailoring:</span>
          <span className="score-value">{matchInfo.tailored}%</span>
        </div>
      </div>

      {/* Tailor vs Use Current */}
      {!tailoredResume && (
        <div className="action-buttons">
          <button
            onClick={handleTailor}
            disabled={tailoring}
            className={`btn-primary ${tailoring ? "btn-disabled" : ""}`}
          >
            {tailoring ? "Tailoring…" : "Tailor Résumé with AI"}
          </button>
          <button
            onClick={() => setTailoredResume(resume)}
            className="btn-secondary"
          >
            Use My Current Résumé
          </button>
        </div>
      )}

      {/* Editor + Downloads + Apply */}
      {tailoredResume && (
        <div className="editor-and-downloads">
          <label htmlFor="resume-editor" className="editor-label">
            Your Résumé (editable):
          </label>
          <textarea
            id="resume-editor"
            className="resume-editor"
            rows={15}
            value={tailoredResume}
            onChange={(e) => setTailoredResume(e.target.value)}
          />

          <div className="download-buttons">
            <button
              onClick={() => handleDownload("pdf")}
              className="btn-outline"
            >
              <FaDownload /> Download PDF
            </button>
            <button
              onClick={() => handleDownload("docx")}
              className="btn-outline"
            >
              <FaDownload /> Download DOCX
            </button>
          </div>

          <button
            onClick={handleAutoApply}
            disabled={applying}
            className="btn-apply"
          >
            {applying ? "Auto-Applying…" : "Auto Apply & Redirect"}
          </button>
        </div>
      )}

      {/* Job Description */}
      <div className="job-description-section">
        <h2 className="section-heading">Job Description</h2>
        <pre className="job-description-text">{job.jd_text}</pre>
      </div>
    </div>
  );
}
