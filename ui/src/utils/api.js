const BASE = "/api";  // proxy'd to FastAPI

// ✅ Upload resume file
export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE}/upload-resume`, {
    method: "POST",
    body: formData,
  });
  return res.json();
};

// ✅ Generate AI-based resume (returns DOCX blob)
export const generateResume = async (name, job_description) => {
  const res = await fetch(`${BASE}/generate-resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, job_description }),
  });
  return res.blob(); // Will be streamed as .docx
};

// ✅ Download resume in PDF
export const downloadPDF = async (resumeText, fileName = "AI_Resume") => {
  const res = await fetch(`${BASE}/download-pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_text: resumeText, file_name: fileName }),
  });
  return res.blob();
};

// ✅ Download resume in DOCX
export const downloadDOCX = async (resumeText, fileName = "AI_Resume") => {
  const res = await fetch(`${BASE}/download-docx`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_text: resumeText, file_name: fileName }),
  });
  return res.blob();
};

export async function matchResumeToJD(resume, jd) {
  const res = await fetch("/match", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume, jd }),
  });
  return res.json();
}

export async function tailorResumeWithAI(resume, jd, role = "Job", company = "Company") {
  const res = await fetch("/tailor", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume, jd, role, company }),
  });
  return res.json();
}
