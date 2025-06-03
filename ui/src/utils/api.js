// Always use your deployed backend URL (never localhost in prod)
const API_BASE = "https://crispy-engine-1.onrender.com";

//
// ─── AUTH ───────────────────────────────────────────────────────────────────────
//
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

//
// ─── ONBOARDING ────────────────────────────────────────────────────────────────
//
export const submitOnboarding = async (data) => {
  const res = await fetch(`${API_BASE}/api/onboarding`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include", // so that cookies/sessions are sent if needed
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Onboarding submission failed");
  }
  return res.json();
};

//
// ─── JOBS / RECOMMENDED ────────────────────────────────────────────────────────
//
export const fetchJobs = async (resume) => {
  const res = await fetch(`${API_BASE}/api/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume, sort_by: "TopMatched" }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Job fetching failed");
  }
  return res.json();
};

//
// ─── INTERVIEW / EVALUATION ───────────────────────────────────────────────────
//
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

//
// ─── RESUME / TAILOR ────────────────────────────────────────────────────────────
//
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
  return res.json();
};

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

//
// ─── AUTO-APPLY ────────────────────────────────────────────────────────────────
//
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
  return res.json();
};

//
// ─── MATCH RESUME/JD ───────────────────────────────────────────────────────────
//
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

//
// ─── JOB DETAIL ────────────────────────────────────────────────────────────────
//
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

//
// ─── LEGACY JOB APPLICATION ────────────────────────────────────────────────────
//
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
