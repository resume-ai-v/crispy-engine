import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { tailorResume, autoApplyJob, downloadPDF, downloadDOCX, getJobDetail } from "../utils/api";
import { FaDownload } from "react-icons/fa";
import "./ApplyPage.css"; // Optional

export default function ApplyPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tailoring, setTailoring] = useState(false);
  const [tailoredResume, setTailoredResume] = useState("");
  const [matchInfo, setMatchInfo] = useState({ original: 0, tailored: 0 });
  const [applying, setApplying] = useState(false);

  const resume = localStorage.getItem("resumeText") || "";

  useEffect(() => {
    async function fetchJobDetailData() {
      setLoading(true);
      try {
        const data = await getJobDetail(id);
        setJob(data);
        setMatchInfo((prev) => ({
          ...prev,
          original: data.match_score || 0,
        }));
      } catch (err) {
        setJob(null);
        console.error("Error fetching job:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchJobDetailData();
  }, [id]);

  if (loading) return <div className="apppage-container">Loading job details…</div>;
  if (!job) return <div className="apppage-container">Job not found.</div>;

  const handleTailor = async () => {
    setTailoring(true);
    try {
      const res = await tailorResume(resume, job.jd_text || job.description, job.title, job.company);
      setTailoredResume(res.tailored_resume || "");
      setMatchInfo({
        original: res.original_match || 0,
        tailored: res.tailored_match || 0,
      });
    } catch (err) {
      alert("❌ Something went wrong while tailoring the résumé.");
    }
    setTailoring(false);
  };

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
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `AI_Resume.${format}`;
      a.click();
      a.remove();
    } catch (err) {
      alert("❌ Download failed. Please try again.");
    }
  };

  const handleAutoApply = async () => {
    setApplying(true);
    try {
      const payload = {
        resume: tailoredResume || resume,
        job_url: job.link || job.url,
        job_title: job.title,
        company: job.company,
      };
      const res = await autoApplyJob(payload);
      window.open(job.link || job.url, "_blank");
    } catch (err) {
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
      <div className="job-subtitle">{job.company} • {job.location}</div>
      <div className="job-type">{job.type}</div>

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

      {tailoredResume && (
        <div className="editor-and-downloads">
          <label htmlFor="resume-editor" className="editor-label">Your Résumé (editable):</label>
          <textarea
            id="resume-editor"
            className="resume-editor"
            rows={15}
            value={tailoredResume}
            onChange={(e) => setTailoredResume(e.target.value)}
          />

          <div className="download-buttons">
            <button onClick={() => handleDownload("pdf")} className="btn-outline">
              <FaDownload /> Download PDF
            </button>
            <button onClick={() => handleDownload("docx")} className="btn-outline">
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

      <div className="job-description-section">
        <h2 className="section-heading">Job Description</h2>
        <pre className="job-description-text">{job.jd_text || job.description}</pre>
      </div>
    </div>
  );
}
