// Always use deployed backend (never localhost)
const API_BASE = "https://crispy-engine-1.onrender.com";
export const API_BASE = "https://crispy-engine-1.onrender.com";

/**
 * Signup (new user)
 */
export const signup = async (full_name, email, password) => {
  const res = await fetch(`${API_BASE}/api/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ full_name, email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Signup failed");
  }
  return res.json();
};

/**
 * Login (real, not dummy)
 */
export const login = async (email, password) => {
  const res = await fetch(`${API_BASE}/api/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Login failed");
  }
  return res.json();
};

/**
 * Resume Upload (multipart/form-data)
 */
export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/upload-resume`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("Resume upload failed");
  return res.json();
};

/**
 * Tailor Resume with GPT
 */
export const tailorResume = async (resume, jd, role = "Generic", company = "Unknown") => {
  const res = await fetch(`${API_BASE}/tailor-resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume, jd, role, company }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Tailor failed");
  }
  return await res.json();
};

/**
 * Download Resume (PDF or DOCX)
 */
export const downloadPDF = async (resumeText) => {
  const res = await fetch(`${API_BASE}/download-resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume: resumeText, format: "pdf" }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "PDF download failed");
  }
  return res.blob();
};

export const downloadDOCX = async (resumeText) => {
  const res = await fetch(`${API_BASE}/download-resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume: resumeText, format: "docx" }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "DOCX download failed");
  }
  return res.blob();
};

/**
 * Auto-Apply to Job
 */
export const autoApplyJob = async ({ resume, job_url, job_title, company }) => {
  const res = await fetch(`${API_BASE}/auto-apply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume, job_url, job_title, company }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Auto-apply failed");
  }
  return await res.json();
};

/**
 * Generate AI-Based Resume (DOCX)
 */
export const generateResume = async (name, job_description) => {
  const res = await fetch(`${API_BASE}/api/generate-resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, job_description }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Resume generation failed");
  }
  return res.blob();
};

/**
 * Match Resume to Job Description
 */
export const matchResumeToJD = async (resume, jd) => {
  const res = await fetch(`${API_BASE}/api/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume, jd }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Resume–JD match failed");
  }
  return res.json();
};

/**
 * Submit Onboarding Details
 */
export const submitOnboarding = async (data) => {
  const res = await fetch(`${API_BASE}/api/onboarding`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
    credentials: "include"
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Onboarding submission failed");
  }
  return res.json();
};

/**
 * Evaluate Interview Answer for Feedback
 */
export const evaluateAnswer = async (answer, jd = "Generic") => {
  const res = await fetch(`${API_BASE}/api/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answer, jd }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Evaluation failed");
  }
  return res.json();
};

/**
 * Fetch AI-Generated Interview Questions
 */
export const fetchInterviewQuestions = async (jobTitle) => {
  const res = await fetch(`${API_BASE}/api/generate-questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_title: jobTitle }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Question generation failed");
  }
  return res.json();
};

/**
 * Fetch Job Listings Based on Resume
 */
export const fetchJobs = async (resume) => {
  const res = await fetch(`${API_BASE}/api/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Job fetching failed");
  }
  return res.json();
};

/**
 * Get Job Details (with GPT Explanation)
 */
export const getJobDetail = async (jobId, resumeText) => {
  const res = await fetch(`${API_BASE}/api/job/${jobId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume: resumeText }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Fetching job detail failed");
  }
  return res.json();
};

/**
 * Legacy “apply to job”
 */
export const applyToJob = async (data) => {
  const res = await fetch(`${API_BASE}/api/apply-to-job`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Job application failed");
  }
  return res.json();
};
