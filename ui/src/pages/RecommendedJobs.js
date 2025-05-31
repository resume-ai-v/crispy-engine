import React, { useState, useEffect } from "react";
import { fetchJobs } from "../utils/api";

const FILTER_OPTIONS = [
  { label: "Top Matched", value: "top" },
  { label: "Most Recent", value: "recent" },
];

export default function RecommendedJobs() {
  const [jobs, setJobs] = useState([]);
  const [filter, setFilter] = useState("top");
  const [loading, setLoading] = useState(true);
  const resume = localStorage.getItem("resumeText");

  const loadJobs = async () => {
    try {
      setLoading(true);
      const response = await fetchJobs({ resume, sort_by: filter });
      setJobs(response || []);
    } catch (error) {
      console.error("Failed to load jobs:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (resume) loadJobs();
  }, [filter]);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Recommended Jobs</h1>

        {/* 🔽 Filter Dropdown */}
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="border border-gray-300 rounded px-3 py-1 text-sm"
        >
          {FILTER_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div>Loading jobs...</div>
      ) : jobs.length === 0 ? (
        <div>No jobs found.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {jobs.map((job) => (
            <div key={job.id} className="bg-white p-4 rounded shadow">
              <h2 className="font-semibold">{job.title}</h2>
              <p className="text-sm text-gray-600">{job.company} • {job.location}</p>
              {job.match_score && (
                <p className="text-xs text-purple-700 mt-1">{job.match_score}% match</p>
              )}
              <a
                href={`/job-detail/${job.id}`}
                className="inline-block mt-3 text-sm text-blue-600 hover:underline"
              >
                View Details →
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
