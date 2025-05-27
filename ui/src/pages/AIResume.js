import React, { useState } from "react";
import Sidebar from "../components/Sidebar";
import {
  uploadResume,
  generateResume
} from "../utils/api"; // centralized API functions

import {
  matchResumeToJD,
  tailorResumeWithAI
} from "../utils/api";


export default function AIResume() {
  const [resumeURL, setResumeURL] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  const userName = localStorage.getItem("userFullName") || "Guest";

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    try {
      const data = await uploadResume(file);
      localStorage.setItem("resumeText", data.parsed_resume);
      setResumeURL("");
      alert("✅ Resume uploaded & parsed successfully!");
    } catch (err) {
      alert("❌ Upload failed.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!name || !jobDesc) return alert("Please enter your name and job description.");

    setLoading(true);
    try {
      const blob = await generateResume(name, jobDesc);
      const url = URL.createObjectURL(blob);
      setResumeURL(url);
      localStorage.setItem("resumeGenerated", url);
    } catch (err) {
      alert("❌ Failed to generate resume.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar active="resume" />
      <main className="flex-1 p-8 overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-xl font-bold text-gray-800">Recommended Jobs</h1>
            <h2 className="text-lg font-semibold text-gray-700 mt-1">AI Resumes</h2>
          </div>
          <div className="relative group">
            <button className="text-sm font-medium text-gray-700 group-hover:text-purple-600">
              {userName} <span className="ml-1">▼</span>
            </button>
            <div className="absolute right-0 mt-2 w-40 bg-white rounded-md shadow-lg hidden group-hover:block z-10">
              <a href="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Profile</a>
              <a href="/settings" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Settings</a>
              <a href="/help" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Help</a>
              <a href="/logout" className="block px-4 py-2 text-sm text-red-600 hover:bg-gray-100">Logout</a>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-8">
          <div className="col-span-1 bg-white p-4 rounded shadow h-full">
            <div className="text-lg font-medium text-gray-700 border-b pb-2 mb-2">Resume Actions</div>

            <div className="mb-4">
              <label className="block text-sm text-gray-600 mb-1">Upload Resume</label>
              <input type="file" onChange={handleUpload} className="text-sm" />
            </div>

            <div className="mb-4">
              <label className="block text-sm text-gray-600 mb-1">Your Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full border px-2 py-1 text-sm rounded"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm text-gray-600 mb-1">Job Description</label>
              <textarea
                rows={5}
                value={jobDesc}
                onChange={(e) => setJobDesc(e.target.value)}
                className="w-full border px-2 py-1 text-sm rounded"
              ></textarea>
            </div>

            <button
              onClick={handleGenerate}
              disabled={loading}
              className="w-full bg-purple-600 text-white py-2 rounded shadow hover:bg-purple-700"
            >
              {loading ? "Generating..." : "Generate AI Resume"}
            </button>
          </div>

          <div className="col-span-2 bg-white p-6 rounded shadow min-h-[80vh]">
            {resumeURL ? (
              <iframe
                src={resumeURL}
                title="AI Resume"
                className="w-full h-[80vh] border rounded-md shadow"
              ></iframe>
            ) : (
              <div className="text-center text-gray-600 text-lg">
                No resume generated yet.
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
