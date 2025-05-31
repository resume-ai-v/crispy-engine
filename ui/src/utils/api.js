const API_BASE = process.env.REACT_APP_API_BASE || "";


// ✅ Upload resume file
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

// ✅ Generate AI-based resume (returns DOCX blob)
export const generateResume = async (name, job_description) => {
  const res = await fetch(`${API_BASE}/api/generate-resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, job_description }),
  });

  if (!res.ok) throw new Error("Resume generation failed");
  return res.blob(); // .docx file
};

// ✅ Download resume as PDF
export const downloadPDF = async (resumeText, fileName = "AI_Resume") => {
  const res = await fetch(`${API_BASE}/api/download-pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_text: resumeText, file_name: fileName }),
  });

  if (!res.ok) throw new Error("PDF download failed");
  return res.blob();
};

// ✅ Download resume as DOCX
export const downloadDOCX = async (resumeText, fileName = "AI_Resume") => {
  const res = await fetch(`${API_BASE}/api/download-docx`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_text: resumeText, file_name: fileName }),
  });

  if (!res.ok) throw new Error("DOCX download failed");
  return res.blob();
};

// ✅ Match resume to job description
export const matchResumeToJD = async (resume, jd) => {
  const res = await fetch(`${API_BASE}/api/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume, jd }),
  });

  if (!res.ok) throw new Error("Resume-JD match failed");
  return res.json();
};

// ✅ Tailor resume using GPT
export const tailorResumeWithAI = async (resume, jd, role = "Job", company = "Company") => {
  const res = await fetch(`${API_BASE}/api/tailor`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume, jd, role, company }),
  });

  if (!res.ok) throw new Error("Resume tailoring failed");
  return res.json();
};

// ✅ Submit onboarding details
export const submitOnboarding = async (data) => {
  const res = await fetch(`${API_BASE}/api/onboarding`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) throw new Error("Onboarding submission failed");
  return res.json();
};

// ✅ Evaluate interview answer for feedback
export const evaluateAnswer = async (answer, jd = "Generic") => {
  const res = await fetch(`${API_BASE}/api/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answer, jd }),
  });

  if (!res.ok) throw new Error("Evaluation failed");
  return res.json();
};

// ✅ Fetch AI-generated interview questions
export const fetchInterviewQuestions = async (jobTitle) => {
  const res = await fetch(`${API_BASE}/api/generate-questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_title: jobTitle }),
  });

  if (!res.ok) throw new Error("Question generation failed");
  return res.json();
};

// ✅ Fetch job listings based on resume
export const fetchJobs = async (resume) => {
  const res = await fetch(`${API_BASE}/api/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume }),
  });

  if (!res.ok) throw new Error("Job fetching failed");
  return res.json();
};

// ✅ Get job details
export const getJobDetail = async (jobId, resumeText) => {
  const res = await fetch(`${API_BASE}/api/job/${jobId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume: resumeText }),
  });

  if (!res.ok) throw new Error("Fetching job detail failed");
  return res.json();
};

// ✅ Apply to job (with tailored resume + autofill)
export const applyToJob = async (data) => {
  const res = await fetch(`${API_BASE}/api/apply-to-job`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) throw new Error("Job application failed");
  return res.json();
};
