import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";

export default function JobDetailView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [matchExplanation, setMatchExplanation] = useState("");
  const [tailored, setTailored] = useState("");
  const [comparison, setComparison] = useState("");
  const [status, setStatus] = useState("");
  const [applying, setApplying] = useState(false);
  const [interviewAssets, setInterviewAssets] = useState({ audio_url: "", video_url: "" });

  const resumeText = localStorage.getItem("resumeText") || "";
  const userName = localStorage.getItem("userFullName") || "User";

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const res = await fetch(`/job/${id}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ resume: resumeText }),
        });
        const data = await res.json();
        setJob(data.job || {});
        setMatchExplanation(data.match_explanation || "");
      } catch (err) {
        console.error("Failed to load job details:", err);
      }
    };
    fetchJob();
  }, [id]);

  const handleTailor = async () => {
    if (!resumeText || !job.jd_text) return alert("Missing resume or job description.");
    setStatus("Tailoring resume...");
    try {
      const res = await fetch("/tailor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume: resumeText,
          jd: job.jd_text,
          role: job.title,
          company: job.company,
        }),
      });
      const data = await res.json();
      setTailored(data.tailored_resume);
      setStatus("✅ Resume tailored!");
    } catch (err) {
      console.error("Tailoring failed:", err);
      setStatus("❌ Failed to tailor resume.");
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const res = await fetch("/download-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_text: tailored, file_name: "Tailored_Resume" }),
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "Tailored_Resume.pdf";
      a.click();
    } catch (err) {
      alert("❌ Failed to download PDF.");
      console.error(err);
    }
  };

  const handleApply = async () => {
    setApplying(true);
    try {
      const res = await fetch("/apply-smart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume: resumeText,
          jd: job.jd_text,
          job_url: job.url,
          role: job.title,
          company: job.company,
          phone_number: "1234567890",
          user_name: userName,
        }),
      });
      const data = await res.json();
      setStatus(data.status || "✅ Applied successfully.");
    } catch (err) {
      setStatus("❌ Application failed.");
      console.error(err);
    } finally {
      setApplying(false);
    }
  };

  const handleStartInterview = async () => {
    try {
      const res = await fetch("/api/start-interview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume: resumeText, jd: job.jd_text, round: "HR" }),
      });
      const data = await res.json();
      setInterviewAssets({ audio_url: data.audio_url, video_url: data.video_url });
    } catch (err) {
      alert("❌ Interview generation failed.");
      console.error(err);
    }
  };

  const handleCompareResumes = async () => {
    try {
      const res = await fetch("/compare-resumes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          original: resumeText,
          tailored: tailored,
          jd: job.jd_text,
        }),
      });
      const data = await res.json();
      setComparison(data.comparison || "No response.");
    } catch (err) {
      alert("❌ Failed to compare resumes.");
      console.error(err);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar active="recommended-jobs" />
      <main className="flex-1 p-8 overflow-y-auto">
        <button
          onClick={() => navigate("/recommended-jobs")}
          className="text-sm text-purple-600 underline mb-4"
        >
          ← Back to Jobs
        </button>

        {job ? (
          <div className="max-w-3xl mx-auto bg-white p-6 rounded shadow">
            <h1 className="text-2xl font-bold text-gray-800">{job.title}</h1>
            <p className="text-gray-600 mb-2">{job.company} | {job.location}</p>

            {/* Match Progress Bar */}
            <div className="mb-4">
              <p className="text-sm text-gray-700">Match Score:</p>
              <div className="w-full bg-gray-200 rounded-full h-4 mt-1">
                <div
                  className="bg-purple-600 h-4 rounded-full text-xs text-white text-center"
                  style={{ width: `${job.match_percentage || 0}%` }}
                >
                  {job.match_percentage ? `${Math.round(job.match_percentage)}%` : "0%"}
                </div>
              </div>
            </div>

            <div className="border-t pt-4 text-gray-700 whitespace-pre-wrap">{job.jd_text}</div>

            {/* Match Explanation */}
            {matchExplanation && (
              <div className="mt-4 text-sm text-blue-900 border-l-4 border-blue-400 bg-blue-50 p-4">
                <strong>Match Explanation:</strong>
                <p>{matchExplanation}</p>
              </div>
            )}

            {/* Tailor Resume */}
            <button
              onClick={handleTailor}
              className="mt-6 bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
            >
              ✨ Tailor Resume
            </button>

            {/* Tailored Resume Preview */}
            {tailored && (
              <div className="mt-6 border rounded bg-gray-50 p-4 text-sm text-gray-800 whitespace-pre-wrap">
                <h3 className="font-semibold mb-2">📄 Tailored Resume Preview</h3>
                {tailored}
                <div className="mt-3 flex gap-3">
                  <button
                    onClick={handleDownloadPDF}
                    className="bg-gray-800 text-white px-3 py-1 rounded hover:bg-gray-900"
                  >
                    ⬇️ Download PDF
                  </button>
                  <button
                    onClick={handleCompareResumes}
                    className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                  >
                    🤖 Compare with Original
                  </button>
                </div>
              </div>
            )}

            {/* AI Explanation Result */}
            {comparison && (
              <div className="mt-6 bg-blue-50 p-4 rounded border-l-4 border-blue-400 text-blue-900 whitespace-pre-wrap text-sm">
                <strong>🔍 AI Comparison:</strong>
                <p className="mt-1">{comparison}</p>
              </div>
            )}

            {/* Apply with Tailored Resume */}
            <button
              onClick={handleApply}
              disabled={applying}
              className="mt-6 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              {applying ? "Applying..." : "🚀 Apply with AI Resume"}
            </button>

            {/* Interview Avatar */}
            <div className="mt-6">
              <button
                onClick={handleStartInterview}
                className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
              >
                🎤 Start AI Interview Preview
              </button>

              {interviewAssets.video_url && (
                <div className="mt-4">
                  <video controls width="100%">
                    <source src={interviewAssets.video_url} type="video/mp4" />
                  </video>
                </div>
              )}

              {interviewAssets.audio_url && (
                <div className="mt-2">
                  <audio controls>
                    <source src={interviewAssets.audio_url} type="audio/mpeg" />
                  </audio>
                </div>
              )}
            </div>

            {status && <p className="mt-4 text-sm text-blue-700 font-medium">{status}</p>}
          </div>
        ) : (
          <p className="text-red-600">Job not found.</p>
        )}
      </main>
    </div>
  );
}
