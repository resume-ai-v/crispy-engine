import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getJobDetail, tailorResumeWithAI } from "../utils/api";

export default function JobDetail() {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tailoring, setTailoring] = useState(false);
  const [step, setStep] = useState(1);
  const navigate = useNavigate();

  const resume = localStorage.getItem("resumeText");

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const result = await getJobDetail(id, resume);
        setJob(result.job);
        localStorage.setItem("selectedJobJD", result.job.jd_text || "");
        localStorage.setItem("selectedJobURL", result.job.url || "");
        localStorage.setItem("matchScore", result.match_score || "");
      } catch (err) {
        console.error("Error fetching job details:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [id]);

  const handleTailorResume = async () => {
    try {
      setTailoring(true);
      const tailored = await tailorResumeWithAI(
        resume,
        job.jd_text,
        job.title,
        job.company
      );
      localStorage.setItem("tailoredResume", tailored.tailored_resume || "");
      navigate("/inline-editor");
    } catch (err) {
      console.error("Tailoring failed", err);
      alert("❌ Failed to tailor resume. Please try again.");
    } finally {
      setTailoring(false);
    }
  };

  if (loading) return <div className="p-8">Loading job details...</div>;
  if (!job) return <div className="p-8">Job not found.</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto bg-white rounded shadow">
      <h2 className="text-2xl font-bold mb-2">{job.title}</h2>
      <p className="text-gray-600 mb-1">{job.company}</p>
      <p className="text-sm text-gray-500 mb-2">{job.location}</p>

      {/* ✅ Display match score */}
      {job.match_score && (
        <div className="inline-block bg-black text-white text-sm px-3 py-1 rounded mb-3">
          {job.match_score}% Match
        </div>
      )}

      {/* ✅ Job Description */}
      <p className="text-md text-gray-800 leading-relaxed whitespace-pre-wrap mb-4">
        {job.jd_text}
      </p>

      {/* ✅ Tailor Option Step 1 */}
      {step === 1 && (
        <div className="mt-6">
          <p className="font-medium mb-2">
            Would you like to tailor your resume for this job?
          </p>
          <button
            onClick={() => setStep(2)}
            className="bg-purple-600 text-white px-4 py-2 rounded mr-4"
          >
            Yes, Tailor It
          </button>
          <button
            onClick={() => window.open(job.url, "_blank")}
            className="border px-4 py-2 rounded"
          >
            No, Apply with Original
          </button>
        </div>
      )}

      {/* ✅ Tailor Resume Step 2 */}
      {step === 2 && (
        <div className="mt-6">
          <p className="text-gray-600 mb-2">
            {tailoring
              ? "✍️ Tailoring resume with AI..."
              : "✍️ Launching inline resume editor..."}
          </p>
          <button
            onClick={handleTailorResume}
            disabled={tailoring}
            className={`px-4 py-2 rounded text-white ${
              tailoring ? "bg-gray-400" : "bg-green-600 hover:bg-green-700"
            }`}
          >
            {tailoring ? "Tailoring..." : "Proceed to Tailor"}
          </button>
        </div>
      )}
    </div>
  );
}
