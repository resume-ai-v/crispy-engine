import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import JobCard from "../components/JobCard";
import UserDropdown from "../components/UserDropdown";

export default function RecommendedJobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  const resumeText = localStorage.getItem("resumeText");

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await fetch("/api/jobs", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ resume: resumeText || "" }),
        });

        const data = await res.json();
        if (Array.isArray(data.jobs)) {
          setJobs(data.jobs);
        } else {
          console.error("Invalid jobs format:", data);
        }
      } catch (error) {
        console.error("Failed to fetch jobs:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar active="recommended-jobs" />

      <main className="flex-1 p-8 overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Recommended Jobs</h1>
          <UserDropdown />
        </div>

        {loading ? (
          <p className="text-gray-600">Loading jobs...</p>
        ) : jobs.length === 0 ? (
          <p className="text-gray-600">No jobs found.</p>
        ) : (
          <div className="grid gap-4">
            {jobs.map((job, index) => (
              <JobCard
                key={index}
                title={job.title}
                company={job.company}
                location={job.location}
                salary={job.salary || "Not specified"}
                match={`${job.match_percentage || "0"}% Match`}
                posted={job.posted || "Recently"}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
