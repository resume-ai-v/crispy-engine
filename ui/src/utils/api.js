export const API_BASE = "https://crispy-engine-nx6e.onrender.com/api";

// --- Helper: Get session-token (MVP, not JWT) ---
export const getToken = () => localStorage.getItem("token");

// --- Helper: Attach Authorization header if token present ---
export const withAuth = (headers = {}) => {
  const token = getToken();
  return token ? { ...headers, Authorization: token } : headers;
};

export const signup = async (first_name, last_name, email, password) => {
  const res = await fetch(`${API_BASE}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      first_name,
      last_name,
      email,
      password,
    }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Signup failed");
  if (data.token) localStorage.setItem("token", data.token); // Save session-token!
  return data;
};

export const login = async (email, password) => {
  const res = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Login failed");
  if (data.token) localStorage.setItem("token", data.token);
  return data;
};

// --- Suggestions (no auth required!) ---

export const suggestSkills = async (query) => {
  const res = await fetch(`${API_BASE}/suggest/skills?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error("Failed to fetch skills");
  return (await res.json()).options || [];
};

export const suggestRoles = async (query) => {
  const res = await fetch(`${API_BASE}/suggest/roles?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error("Failed to fetch roles");
  return (await res.json()).options || [];
};

export const suggestCities = async (query) => {
  const res = await fetch(`${API_BASE}/suggest/cities?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error("Failed to fetch cities");
  return (await res.json()).options || [];
};

// --- Onboarding (auth required) ---

export const submitOnboarding = async (data) => {
  const res = await fetch(`${API_BASE}/onboarding`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify(data),
  });
  const result = await res.json();
  if (!res.ok) throw new Error(result.detail || "Onboarding submission failed");
  return result;
};

export const getOnboarding = async () => {
  const res = await fetch(`${API_BASE}/onboarding`, {
    method: "GET",
    headers: withAuth(),
  });
  if (!res.ok) return {};
  return res.json();
};

// --- Resume Upload (auth required) ---
export const uploadResume = async (file) => {
  if (!file) throw new Error("No file selected for upload.");
  const formData = new FormData();
  formData.append("file", file);

  if (process.env.NODE_ENV === "development") {
    console.log("[uploadResume] uploading file:", file);
  }

  const res = await fetch(`${API_BASE}/upload-resume`, {
    method: "POST",
    headers: withAuth(),
    body: formData,
  });

  if (!res.ok) throw new Error("Resume upload failed");
  return res.json();
};

// --- Download Resume (PDF/DOCX) ---
export const downloadPDF = async (resumeText) => {
  if (!resumeText || !resumeText.trim()) throw new Error("No resume text provided for PDF download.");
  const res = await fetch(`${API_BASE}/download-resume`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify({ resume: resumeText, format: "pdf" }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "PDF download failed");
  }
  return res.blob();
};

export const downloadDOCX = async (resumeText) => {
  if (!resumeText || !resumeText.trim()) throw new Error("No resume text provided for DOCX download.");
  const res = await fetch(`${API_BASE}/download-resume`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify({ resume: resumeText, format: "docx" }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "DOCX download failed");
  }
  return res.blob();
};

// --- Tailor Resume (auto-trim to 6000 chars) ---
const MAX_TAILOR_LENGTH = 6000;
function trimToLength(text, maxLen = MAX_TAILOR_LENGTH) {
  if (!text) return "";
  return text.length > maxLen ? text.slice(0, maxLen) : text;
}

export const tailorResume = async (resume, jd, role = "Generic", company = "Unknown") => {
  if (!resume || !resume.trim()) throw new Error("No resume provided for tailoring.");
  if (!jd || !jd.trim()) throw new Error("No job description provided for tailoring.");

  const safeResume = trimToLength(resume);
  const safeJD = trimToLength(jd);

  if (resume.length > MAX_TAILOR_LENGTH || jd.length > MAX_TAILOR_LENGTH) {
    alert(
      "Resume or Job Description was too long and has been automatically trimmed to 6000 characters for tailoring. For best results, consider making them shorter and more focused."
    );
  }

  const payload = { resume: safeResume, jd: safeJD, role, company };

  const res = await fetch(`${API_BASE}/tailor-resume`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    let err = {};
    try {
      err = await res.json();
    } catch {}
    if (
      res.status === 429 ||
      (err.detail && err.detail.toLowerCase().includes("quota"))
    ) {
      throw new Error(
        "AI tailoring service is temporarily unavailable (OpenAI quota exceeded or too many requests). Please try again later."
      );
    }
    throw new Error(err.detail || "Tailor failed");
  }
  return await res.json();
};


// --- Fetch Jobs ---
export const fetchJobs = async (resume, preferredRoles = [], preferredCities = [], employmentTypes = []) => {
  if (!resume || !resume.trim()) throw new Error("Resume is required for job search.");
  const res = await fetch(`${API_BASE}/jobs`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify({ resume, preferredRoles, preferredCities, employmentTypes }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Job fetching failed");
  }
  return res.json();
};

// --- Job Detail ---
export const getJobDetail = async (jobId, resumeText) => {
  if (!resumeText || !resumeText.trim()) throw new Error("Resume text required for job detail.");
  const res = await fetch(`${API_BASE}/job/${jobId}`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify({ resume: resumeText }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Fetching job detail failed");
  }
  return res.json();
};

// --- AI Resume Generation ---
export const generateResume = async (name, job_description) => {
  if (!name || !job_description) throw new Error("Name and job description required.");
  const res = await fetch(`${API_BASE}/generate-resume`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify({ name, job_description }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Resume generation failed");
  }
  return res.blob();
};

// --- Match Resume to JD ---
export const matchResumeToJD = async (resume, jd) => {
  if (!resume || !resume.trim() || !jd || !jd.trim()) throw new Error("Both resume and job description are required.");
  const res = await fetch(`${API_BASE}/match`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify({ resume, jd }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Resume–JD match failed");
  }
  return res.json();
};

// --- Interview & Feedback ---
export const evaluateAnswer = async (answer, jd = "Generic") => {
  if (!answer || !answer.trim()) throw new Error("Answer is required for evaluation.");
  const res = await fetch(`${API_BASE}/evaluate`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify({ answer, jd }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Evaluation failed");
  }
  return res.json();
};

export const fetchInterviewQuestions = async (jobTitle) => {
  if (!jobTitle || !jobTitle.trim()) throw new Error("Job title required for interview questions.");
  const res = await fetch(`${API_BASE}/generate-questions`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify({ job_title: jobTitle }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Question generation failed");
  }
  return res.json();
};

// --- Auto-Apply to Job ---
export const autoApplyJob = async ({ resume, job_url, job_title, company }) => {
  if (!resume || !resume.trim() || !job_url) throw new Error("Resume and job URL required for auto-apply.");
  const res = await fetch(`${API_BASE}/auto-apply`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify({ resume, job_url, job_title, company }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Auto-apply failed");
  }
  return await res.json();
};

// --- Cover Letter Generation ---
export const generateCoverLetter = async (data) => {
  if (!data || !data.resume || !data.jd) throw new Error("Resume and job description are required.");
  const res = await fetch(`${API_BASE}/generate-cover-letter`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to generate cover letter.");
  }
  return res.json();
};
