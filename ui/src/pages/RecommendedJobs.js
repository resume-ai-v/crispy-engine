import React, { useEffect, useState } from "react";
import JobCard from "../components/JobCard";
import { fetchJobs } from "../utils/api";

export default function RecommendedJobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Assume the user’s resume text was stored in localStorage
  const resume = localStorage.getItem("resumeText") || "";

  useEffect(() => {
    async function loadJobs() {
      setLoading(true);
      setError("");
      try {
        const data = await fetchJobs(resume);
        setJobs(data);
      } catch (err) {
        setError(err.message || "Unknown error");
      }
      setLoading(false);
    }
    loadJobs();
  }, [resume]);

  return (
    <div className="p-8 w-full min-h-screen bg-gray-50">
      <div className="flex flex-row justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Recommended Jobs</h1>
          <div className="text-gray-600 mt-2">
            <span className="font-semibold">{jobs.length} Jobs Found</span>
            <br />
            <span>All match your job preferences</span>
          </div>
        </div>
        <button
          className="flex items-center px-4 py-2 rounded-lg border font-medium shadow-sm text-gray-700 hover:bg-gray-100"
          onClick={() => alert("Edit Preferences coming soon!")}
        >
          <span className="mr-2">Edit Preferences</span>
          <svg width="20" height="20" fill="none" stroke="currentColor">
            <path d="M3 6h13M3 12h13M3 18h13" />
          </svg>
        </button>
      </div>

      {error && <div className="text-red-600">{error}</div>}

      {loading ? (
        <div className="text-lg py-8 text-center">Loading...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 mt-2">
          {jobs.map((job) => (
            <JobCard key={job.id + job.company} job={job} />
          ))}
        </div>
      )}
    </div>
  );
}
