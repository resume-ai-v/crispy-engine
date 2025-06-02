import React, { useState } from "react";
import { tailorResume, downloadResume, autoApplyJob } from "../utils/api";

export default function ApplyModal({ job, resume, onClose }) {
  const [step, setStep] = useState(1);
  const [tailoredResume, setTailoredResume] = useState("");
  const [matchInfo, setMatchInfo] = useState({ old: 0, new: 0 });
  const [downloading, setDownloading] = useState(false);
  const [applying, setApplying] = useState(false);

  const handleTailor = async () => {
    setStep(2);
    const res = await tailorResume(resume, job.jd_text, job.title, job.company);
    setTailoredResume(res.tailored_resume);
    setMatchInfo({ old: res.original_match, new: res.tailored_match });
    setStep(3);
  };

  const handleDownload = async (format) => {
    setDownloading(true);
    await downloadResume(tailoredResume || resume, format);
    setDownloading(false);
  };

  const handleAutoApply = async () => {
    setApplying(true);
    await autoApplyJob({
      resume: tailoredResume || resume,
      job_url: job.url,
      job_title: job.title,
      company: job.company,
    });
    setApplying(false);
    window.open(job.url, "_blank");
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/30 z-40">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-xl relative">
        <button onClick={onClose} className="absolute right-4 top-4 text-xl">✕</button>
        <h2 className="text-2xl font-bold mb-2">{job.title}</h2>
        <p className="text-gray-700">{job.company} • {job.location}</p>
        <div className="text-sm text-gray-500 mb-3">{job.type}</div>
        <pre className="bg-gray-50 p-3 rounded-lg text-sm mb-4 overflow-x-auto" style={{maxHeight: 180}}>{job.jd_text}</pre>
        {step === 1 && (
          <>
            <div className="mb-4">
              <b>How do you want to apply?</b>
            </div>
            <div className="flex gap-4">
              <button className="bg-purple-600 text-white rounded px-4 py-2" onClick={handleTailor}>
                Tailor Resume with AI
              </button>
              <button className="border rounded px-4 py-2" onClick={() => setStep(3)}>
                Use My Current Resume
              </button>
            </div>
          </>
        )}
        {step === 2 && (
          <div className="my-4 text-center">
            <span className="text-purple-600 font-semibold">Tailoring your resume for this job...</span>
          </div>
        )}
        {step === 3 && (
          <>
            <div className="mb-3">
              <div className="flex items-center gap-4">
                <div>
                  <span className="font-medium">Match Score:</span>
                  <span className="ml-2 text-black">
                    {matchInfo.new || matchInfo.old}% Match
                  </span>
                  {tailoredResume && (
                    <span className="ml-2 text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                      {matchInfo.new - matchInfo.old > 0 ? `+${matchInfo.new - matchInfo.old}% Improved` : ""}
                    </span>
                  )}
                </div>
              </div>
              <div className="my-2">
                <button
                  disabled={downloading}
                  className="mr-2 bg-gray-200 px-4 py-2 rounded hover:bg-gray-300"
                  onClick={() => handleDownload("pdf")}
                >
                  Download as PDF
                </button>
                <button
                  disabled={downloading}
                  className="bg-gray-200 px-4 py-2 rounded hover:bg-gray-300"
                  onClick={() => handleDownload("docx")}
                >
                  Download as DOCX
                </button>
              </div>
            </div>
            <div className="mb-2">
              <button
                disabled={applying}
                className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded font-bold"
                onClick={handleAutoApply}
              >
                {applying ? "Auto-Applying..." : "Auto Apply & Redirect"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
