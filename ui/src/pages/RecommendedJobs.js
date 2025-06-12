import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import JobCard from "../components/JobCard";
import { fetchJobs, getOnboarding } from "../utils/api";

export default function RecommendedJobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadJobs() {
      setLoading(true);
      setError("");
      try {
        // Fetch user's latest onboarding data
        const onboardingData = await getOnboarding();

        // Map fields to camelCase as required by backend
        const resume = onboardingData.resume_text || onboardingData.resume || "";
        const preferredRoles = onboardingData.preferred_roles || onboardingData.preferredRoles || [];
        const preferredCities = onboardingData.preferred_cities || onboardingData.preferredCities || [];
        const employmentTypes = onboardingData.employment_types || onboardingData.employmentTypes || [];

        // Debug log
        console.log("Requesting jobs with:", { resume, preferredRoles, preferredCities, employmentTypes });

        if (!resume) {
          setError("Please complete your profile and upload a resume to get job recommendations.");
          setLoading(false);
          return;
        }

        // Fetch jobs
        const data = await fetchJobs(
          resume,
          preferredRoles,
          preferredCities,
          employmentTypes
        );
        setJobs(data.jobs || []);
      } catch (err) {
        console.error("Error fetching recommended jobs:", err);
        setError(err.message || "Could not fetch job recommendations.");
      } finally {
        setLoading(false);
      }
    }
    loadJobs();
  }, []);

  return (
    <div className="p-4 md:p-8 w-full min-h-screen bg-gray-50">
      <div className="flex flex-row justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Recommended Jobs</h1>
          <div className="text-gray-600 mt-2">
            {loading ? (
              <span>Loading...</span>
            ) : (
              <>
                <span className="font-semibold">{jobs.length} Jobs Found</span>
                <br />
                <span>All match your job preferences</span>
              </>
            )}
          </div>
        </div>
        <Link to="/profile" className="flex items-center px-4 py-2 rounded-lg border font-medium shadow-sm text-gray-700 hover:bg-gray-100">
          <span className="mr-2">Edit Preferences</span>
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 6h18M3 12h18M3 18h18" />
          </svg>
        </Link>
      </div>

      {error && <div className="p-4 text-center text-red-600 bg-red-100 rounded-lg">{error}</div>}

      {loading ? (
        <div className="text-lg py-8 text-center">Finding the best jobs for you...</div>
      ) : (
        <>
          {jobs.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mt-2">
              {jobs.map((job) => (
                <JobCard key={job.id || `${job.title}-${job.company}`} job={job} />
              ))}
            </div>
          ) : (
            !error && (
              <div className="text-center p-8 mt-4 bg-white rounded-lg shadow-sm">
                <p>No job recommendations found at the moment.</p>
                <p className="text-sm text-gray-500 mt-2">
                  Try updating your <Link to="/profile" className="text-blue-500 hover:underline">profile and preferences</Link> to get better matches.
                </p>
              </div>
            )
          )}
        </>
      )}
    </div>
  );
}
