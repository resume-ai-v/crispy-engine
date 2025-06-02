import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { downloadPDF, downloadDOCX } from "../utils/api";

export default function InlineEditor() {
  const [resume, setResume] = useState("");
  const [fileName, setFileName] = useState("Tailored_Resume");
  const navigate = useNavigate();

  useEffect(() => {
    const storedResume = localStorage.getItem("tailoredResumeText") || localStorage.getItem("resumeText");
    if (!storedResume) {
      alert("No resume loaded. Redirecting to Resume page.");
      navigate("/ai-resume");
    } else {
      setResume(storedResume);
    }
  }, [navigate]);

  const handleDownload = async (type) => {
    try {
      const blob = type === "pdf"
        ? await downloadPDF(resume, fileName)
        : await downloadDOCX(resume, fileName);

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${fileName}.${type}`;
      a.click();
    } catch (err) {
      alert("❌ Download failed. Try again.");
      console.error(err);
    }
  };

  const handleChange = (e) => setResume(e.target.value);

  const jobURL = localStorage.getItem("selectedJobURL");

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-purple-700">✍️ Edit Your Tailored Resume</h1>
        <div className="flex gap-2">
          <button
            onClick={() => navigate(-1)}
            className="border border-gray-400 px-4 py-1 rounded hover:bg-gray-100"
          >
            ← Back to Job
          </button>
          {jobURL && (
            <button
              onClick={() => window.open(jobURL, "_blank")}
              className="bg-purple-600 text-white px-4 py-1 rounded hover:bg-purple-700"
            >
              Apply Now
            </button>
          )}
        </div>
      </div>

      <textarea
        className="w-full h-[500px] p-4 border border-gray-300 rounded shadow-sm font-mono text-base whitespace-pre-wrap"
        value={resume}
        onChange={handleChange}
      />

      <div className="mt-6 flex items-center gap-4">
        <input
          type="text"
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
          placeholder="File name"
          className="border px-3 py-2 rounded w-60"
        />
        <button
          onClick={() => handleDownload("pdf")}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Download PDF
        </button>
        <button
          onClick={() => handleDownload("docx")}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Download DOCX
        </button>
      </div>
    </div>
  );
}
