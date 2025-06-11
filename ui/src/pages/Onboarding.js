import React, { useState, useEffect } from "react";
import AsyncSelect from "react-select/async";
import onboardingImage from "../assets/onboarding-image.jpg";
import { submitOnboarding, getOnboarding, API_BASE } from "../utils/api"; // Import API_BASE
import { useNavigate } from "react-router-dom";

// Async loader for react-select (corrected)
const fetchOptions = (endpoint) => async (input) => {
  if (!input || input.length < 2) return [];
  let options = [];
  try {
    if (endpoint === "skills") options = await suggestSkills(input);
    else if (endpoint === "roles") options = await suggestRoles(input);
    else if (endpoint === "cities") options = await suggestCities(input);
    return (options || []).map((val) => ({ value: val, label: val }));
  } catch {
    return [];
  }
};

// Dynamic async options loader for skills, roles, and cities (FIXED)
const fetchOptions = (endpoint) => async (input) => {
  if (!input || input.length < 2) return [];
  try {
    // FIX: Use the API_BASE constant for a reliable URL
    const res = await fetch(`${API_BASE}/api/suggest/${endpoint}?q=${encodeURIComponent(input)}`);
    const data = await res.json();
    return (data.options || []).map((val) => ({ value: val, label: val }));
  } catch {
    return [];
  }
};

export default function Onboarding() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [firstStepSelections, setFirstStepSelections] = useState([]);
  const [educationStatus, setEducationStatus] = useState("");
  const [fieldOfStudy, setFieldOfStudy] = useState("");
  const [skills, setSkills] = useState([]);
  const [resume, setResume] = useState(null);
  const [preferredRoles, setPreferredRoles] = useState([]);
  const [employmentTypes, setEmploymentTypes] = useState([]);
  const [preferredCities, setPreferredCities] = useState([]);
  const [showModal, setShowModal] = useState(false);

  // The rest of your component logic remains the same...
  // Prefill onboarding data if it exists
  useEffect(() => {
    async function load() {
      try {
        const data = await getOnboarding();
        if (data && Object.keys(data).length) {
          setFirstStepSelections(data.firstStepSelections || []);
          setEducationStatus(data.educationStatus || "");
          setFieldOfStudy(data.fieldOfStudy || "");
          setSkills((data.skills || []).map(s => ({ value: s, label: s })));
          setPreferredRoles((data.preferredRoles || []).map(r => ({ value: r, label: r })));
          setEmploymentTypes(data.employmentTypes || []);
          setPreferredCities((data.preferredCities || []).map(c => ({ value: c, label: c })));
        }
      } catch {/* ignore */}
    }
    load();
  }, []);

  const handleCheckboxToggle = (value) => {
    setFirstStepSelections((prev) =>
      prev.includes(value) ? prev.filter((item) => item !== value) : [...prev, value]
    );
  };

  const handleEmploymentTypeToggle = (value) => {
    setEmploymentTypes((prev) =>
      prev.includes(value) ? prev.filter((type) => type !== value) : [...prev, value]
    );
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      setResume(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        localStorage.setItem("resumeFile", reader.result);
        localStorage.setItem("resumeName", file.name);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    const onboardingData = {
      firstStepSelections,
      educationStatus,
      fieldOfStudy,
      skills: skills.map((s) => s.value),
      resumeName: resume?.name || "No resume",
      preferredRoles: preferredRoles.map((r) => r.value),
      employmentTypes,
      preferredCities: preferredCities.map((c) => c.value),
    };

    try {
      const result = await submitOnboarding(onboardingData);
      if (result.status === "success") {
        setShowModal(true);
      } else {
        alert("Something went wrong while saving your onboarding info.");
      }
    } catch (error) {
      console.error("Onboarding error:", error);
      alert("❌ Server error. Please try again.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white text-center px-4 relative">
      <div className="absolute top-6 w-full flex justify-center">
        <h1 className="text-2xl font-bold">
          <span className="text-purple-600">Launch</span>
          <span className="text-gray-900">Hire</span>
        </h1>
      </div>

      {step === 1 && (
        <div className="flex flex-col md:flex-row items-center justify-between max-w-4xl w-full gap-10 mt-20">
          <div className="flex-1 text-left">
            <h2 className="text-3xl font-bold mb-4">Let’s Land Your First Job Faster with AI</h2>
            <p className="text-gray-600 mb-6">
              Smart job matching. AI interviews. Instant resume tailoring.
            </p>
            <button
              onClick={() => setStep(2)}
              className="bg-purple-600 text-white px-6 py-2 rounded hover:bg-purple-700"
            >
              Let's Go!
            </button>
          </div>
          <div className="flex-1">
            <img src={onboardingImage} alt="AI Assistant" className="rounded-lg" />
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="mt-28 max-w-xl w-full">
          <h2 className="text-xl font-bold mb-2">What’s Your First Step Toward Success?</h2>
          <p className="text-gray-600 mb-6">
            Whether you're job hunting, practicing interviews, or polishing your resume we'll guide you every step.
          </p>
          <div className="flex gap-3 justify-center mb-6">
            {["Find my First Job", "Practice Interviews", "Build My Resume"].map((item) => (
              <button
                key={item}
                className={`border px-4 py-2 rounded-full text-sm transition-all duration-150 ${
                  firstStepSelections.includes(item)
                    ? "bg-purple-100 text-purple-600 border-purple-600"
                    : "text-gray-600 border-gray-300"
                }`}
                onClick={() => handleCheckboxToggle(item)}
              >
                {item}
              </button>
            ))}
          </div>
          <div className="flex justify-center gap-4">
            <button onClick={() => setStep(1)} className="bg-gray-200 px-6 py-2 rounded">
              Back
            </button>
            <button onClick={() => setStep(3)} className="bg-purple-600 text-white px-6 py-2 rounded">
              Next
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="mt-28 max-w-xl w-full text-left">
          <h2 className="text-xl font-bold mb-2">Help Us Know You Better.</h2>
          <p className="text-gray-600 mb-6">
            A few quick details so we can show you the most relevant jobs and best practice interviews.
          </p>
          <div className="space-y-4">
            <select
              value={educationStatus}
              onChange={(e) => setEducationStatus(e.target.value)}
              className="w-full border border-gray-300 p-2 rounded"
            >
              <option value="">Select Education Status</option>
              <option value="Undergraduate">Undergraduate</option>
              <option value="Post Graduation">Post Graduation</option>
              <option value="PhD">PhD</option>
            </select>
            <select
              value={fieldOfStudy}
              onChange={(e) => setFieldOfStudy(e.target.value)}
              className="w-full border border-gray-300 p-2 rounded"
            >
              <option value="">Select Field of Study</option>
              <option value="Engineering">Engineering</option>
              <option value="Business">Business</option>
              <option value="Design">Design</option>
            </select>
            <AsyncSelect
              isMulti
              cacheOptions
              defaultOptions
              loadOptions={fetchOptions("skills")}
              value={skills}
              onChange={setSkills}
              placeholder="Search & select your top skills"
            />
            <div className="mt-4">
              <label className="block text-sm mb-1 font-medium text-gray-700">
                Upload Resume (PDF only)
              </label>
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileUpload}
                className="w-full border border-gray-300 p-2 rounded"
              />
            </div>
          </div>
          <div className="flex justify-center gap-4 mt-6">
            <button onClick={() => setStep(2)} className="bg-gray-200 px-6 py-2 rounded">
              Back
            </button>
            <button onClick={() => setStep(4)} className="bg-purple-600 text-white px-6 py-2 rounded">
              Next
            </button>
          </div>
        </div>
      )}

      {step === 4 && (
        <div className="mt-28 max-w-xl w-full text-left">
          <h2 className="text-xl font-bold mb-2">Dream Job? Let’s Find It Together.</h2>
          <p className="text-gray-600 mb-6">Choose the roles and cities you love, we’ll find the best matches for you.</p>

          <div className="space-y-4">
            <AsyncSelect
              isMulti
              cacheOptions
              defaultOptions
              loadOptions={fetchOptions("roles")}
              value={preferredRoles}
              onChange={setPreferredRoles}
              placeholder="Search & select preferred job roles"
            />

            <div className="flex gap-3">
              {["Remote", "Hybrid", "Onsite"].map((type) => (
                <button
                  key={type}
                  className={`px-4 py-2 rounded-full border text-sm ${
                    employmentTypes.includes(type)
                      ? "bg-purple-100 text-purple-600 border-purple-600"
                      : "text-gray-600 border-gray-300"
                  }`}
                  onClick={() => handleEmploymentTypeToggle(type)}
                >
                  {type}
                </button>
              ))}
            </div>

            <AsyncSelect
              isMulti
              cacheOptions
              defaultOptions
              loadOptions={fetchOptions("cities")}
              value={preferredCities}
              onChange={setPreferredCities}
              placeholder="Search & select preferred cities"
            />
          </div>

          <div className="flex justify-center gap-4 mt-6">
            <button onClick={() => setStep(3)} className="bg-gray-200 px-6 py-2 rounded">
              Back
            </button>
            <button onClick={handleSubmit} className="bg-purple-600 text-white px-6 py-2 rounded">
              Submit
            </button>
          </div>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white p-8 rounded-lg shadow-lg text-center max-w-md w-full">
            <div className="text-5xl text-purple-600 mb-4">✓</div>
            <h2 className="text-xl font-bold mb-2">You’re Ready. Let’s Get You Hired.</h2>
            <p className="text-gray-600 mb-6">
              Your dashboard is ready with job matches, interview practices, and resume boosters. Take your first step today!
            </p>
            <button
              onClick={() => navigate("/recommended-jobs")}
              className="bg-purple-600 text-white px-6 py-2 rounded"
            >
              Explore Job Board
            </button>
          </div>
        </div>
      )}
    </div>
  );
}