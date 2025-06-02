import React, { useState, useEffect } from "react";
import { FaArrowLeft, FaDownload, FaPlus, FaTrash } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { downloadPDF, downloadDOCX } from "../utils/api";

const emptyEducation = { degree: "", school: "", location: "", date: "", details: "" };
const emptyExperience = { title: "", company: "", location: "", date: "", details: "" };
const emptyProject = { name: "", tech: "", link: "", description: "" };

export default function ResumeEditor() {
  const navigate = useNavigate();
  const [resume, setResume] = useState({
    fullName: "",
    emailPhone: "",
    linkedin: "",
    github: "",
    summary: "",
    education: [ { ...emptyEducation } ],
    experience: [ { ...emptyExperience } ],
    projects: [ { ...emptyProject } ]
  });
  const [fileName, setFileName] = useState("AI_Resume");
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("resumeEditorData");
    if (stored) setResume(JSON.parse(stored));
  }, []);
  useEffect(() => {
    localStorage.setItem("resumeEditorData", JSON.stringify(resume));
  }, [resume]);

  // Handler helpers
  const handleField = (field, value) => setResume(r => ({ ...r, [field]: value }));
  const handleEdu = (idx, key, value) => setResume(r => ({
    ...r,
    education: r.education.map((e, i) => i === idx ? { ...e, [key]: value } : e)
  }));
  const addEducation = () => setResume(r => ({ ...r, education: [ ...r.education, { ...emptyEducation } ] }));
  const removeEducation = idx => setResume(r => ({ ...r, education: r.education.filter((_, i) => i !== idx) }));
  const handleExp = (idx, key, value) => setResume(r => ({
    ...r,
    experience: r.experience.map((e, i) => i === idx ? { ...e, [key]: value } : e)
  }));
  const addExperience = () => setResume(r => ({ ...r, experience: [ ...r.experience, { ...emptyExperience } ] }));
  const removeExperience = idx => setResume(r => ({ ...r, experience: r.experience.filter((_, i) => i !== idx) }));
  const handleProj = (idx, key, value) => setResume(r => ({
    ...r,
    projects: r.projects.map((p, i) => i === idx ? { ...p, [key]: value } : p)
  }));
  const addProject = () => setResume(r => ({ ...r, projects: [ ...r.projects, { ...emptyProject } ] }));
  const removeProject = idx => setResume(r => ({ ...r, projects: r.projects.filter((_, i) => i !== idx) }));

  // Download with loading state
  const handleDownload = async (type) => {
    const text = renderPlainText(resume);
    setDownloading(true);
    try {
      let blob;
      if (type === "pdf") blob = await downloadPDF(text, fileName);
      else blob = await downloadDOCX(text, fileName);

      // Actually download the file!
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${fileName}.${type}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("❌ Download failed.");
      console.error(err);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="flex justify-center items-start min-h-screen bg-gray-50 py-8 px-2">
      <div className="w-full max-w-3xl bg-white rounded-2xl shadow p-8 flex flex-col gap-6">
        {/* Top: Back + Title + Download */}
        <div className="flex justify-between items-center mb-2">
          <button
            className="flex items-center gap-2 text-gray-600 hover:text-purple-700 text-sm"
            onClick={() => navigate(-1)}
          >
            <FaArrowLeft /> Back
          </button>
          <h1 className="text-2xl font-bold text-purple-700 flex-1 text-center -ml-10">
            Resume Editor
          </h1>
          <div className="flex gap-2">
            <button
              className="bg-purple-100 text-purple-700 px-4 py-2 rounded font-semibold flex items-center gap-2 hover:bg-purple-200"
              onClick={() => handleDownload("pdf")}
              disabled={downloading}
            >
              <FaDownload /> PDF
            </button>
            <button
              className="bg-purple-100 text-purple-700 px-4 py-2 rounded font-semibold flex items-center gap-2 hover:bg-purple-200"
              onClick={() => handleDownload("docx")}
              disabled={downloading}
            >
              <FaDownload /> DOCX
            </button>
          </div>
        </div>

        {/* Contact */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 border-b pb-4">
          <input
            className="font-bold text-2xl border-none outline-none w-full"
            placeholder="Full Name"
            value={resume.fullName}
            onChange={e => handleField("fullName", e.target.value)}
            style={{ borderBottom: "2px solid #222" }}
          />
          <input
            className="border-none outline-none text-lg w-full"
            placeholder="Email / Phone"
            value={resume.emailPhone}
            onChange={e => handleField("emailPhone", e.target.value)}
            style={{ borderBottom: "2px solid #BBB" }}
          />
          <input
            className="col-span-2 border-none outline-none mt-1 text-base w-full"
            placeholder="LinkedIn URL"
            value={resume.linkedin}
            onChange={e => handleField("linkedin", e.target.value)}
            style={{ borderBottom: "2px solid #AAA" }}
          />
          <input
            className="col-span-2 border-none outline-none mt-1 text-base w-full"
            placeholder="GitHub URL"
            value={resume.github}
            onChange={e => handleField("github", e.target.value)}
            style={{ borderBottom: "2px solid #AAA" }}
          />
        </div>

        {/* SUMMARY */}
        <div>
          <div className="text-lg font-bold text-purple-700 mb-1">SUMMARY</div>
          <textarea
            className="w-full min-h-[60px] bg-gray-50 border border-purple-100 rounded-lg p-3 mb-1 focus:ring-2 focus:ring-purple-200"
            placeholder="Short professional summary..."
            value={resume.summary}
            onChange={e => handleField("summary", e.target.value)}
          />
        </div>

        {/* EDUCATION */}
        <div>
          <div className="flex items-center justify-between">
            <div className="text-lg font-bold text-purple-700 mb-1">EDUCATION</div>
            <button className="text-purple-700 text-sm flex items-center gap-1" onClick={addEducation}>
              <FaPlus /> Add
            </button>
          </div>
          <div className="flex flex-col gap-3">
            {resume.education.map((edu, idx) => (
              <div key={idx} className="rounded-lg border border-gray-200 bg-gray-50 p-4 relative">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input
                    className="border-b border-purple-200 py-1 px-2 outline-none"
                    placeholder="Degree"
                    value={edu.degree}
                    onChange={e => handleEdu(idx, "degree", e.target.value)}
                  />
                  <input
                    className="border-b border-purple-200 py-1 px-2 outline-none"
                    placeholder="School"
                    value={edu.school}
                    onChange={e => handleEdu(idx, "school", e.target.value)}
                  />
                  <input
                    className="border-b border-purple-100 py-1 px-2 outline-none"
                    placeholder="Location"
                    value={edu.location}
                    onChange={e => handleEdu(idx, "location", e.target.value)}
                  />
                  <input
                    className="border-b border-purple-100 py-1 px-2 outline-none"
                    placeholder="Date"
                    value={edu.date}
                    onChange={e => handleEdu(idx, "date", e.target.value)}
                  />
                </div>
                <textarea
                  className="w-full mt-2 border border-purple-100 rounded p-2 bg-white text-sm focus:ring"
                  placeholder="Details, activities, honors…"
                  value={edu.details}
                  onChange={e => handleEdu(idx, "details", e.target.value)}
                />
                {resume.education.length > 1 && (
                  <button
                    className="absolute top-2 right-2 text-gray-400 hover:text-red-500"
                    onClick={() => removeEducation(idx)}
                  >
                    <FaTrash />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* EXPERIENCE */}
        <div>
          <div className="flex items-center justify-between">
            <div className="text-lg font-bold text-purple-700 mb-1">EMPLOYMENT EXPERIENCE</div>
            <button className="text-purple-700 text-sm flex items-center gap-1" onClick={addExperience}>
              <FaPlus /> Add
            </button>
          </div>
          <div className="flex flex-col gap-3">
            {resume.experience.map((exp, idx) => (
              <div key={idx} className="rounded-lg border border-gray-200 bg-gray-50 p-4 relative">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input
                    className="border-b border-purple-200 py-1 px-2 outline-none"
                    placeholder="Job Title"
                    value={exp.title}
                    onChange={e => handleExp(idx, "title", e.target.value)}
                  />
                  <input
                    className="border-b border-purple-200 py-1 px-2 outline-none"
                    placeholder="Company"
                    value={exp.company}
                    onChange={e => handleExp(idx, "company", e.target.value)}
                  />
                  <input
                    className="border-b border-purple-100 py-1 px-2 outline-none"
                    placeholder="Location"
                    value={exp.location}
                    onChange={e => handleExp(idx, "location", e.target.value)}
                  />
                  <input
                    className="border-b border-purple-100 py-1 px-2 outline-none"
                    placeholder="Date"
                    value={exp.date}
                    onChange={e => handleExp(idx, "date", e.target.value)}
                  />
                </div>
                <textarea
                  className="w-full mt-2 border border-purple-100 rounded p-2 bg-white text-sm focus:ring"
                  placeholder="Describe your achievements, projects, or impact…"
                  value={exp.details}
                  onChange={e => handleExp(idx, "details", e.target.value)}
                />
                {resume.experience.length > 1 && (
                  <button
                    className="absolute top-2 right-2 text-gray-400 hover:text-red-500"
                    onClick={() => removeExperience(idx)}
                  >
                    <FaTrash />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* PROJECTS */}
        <div>
          <div className="flex items-center justify-between">
            <div className="text-lg font-bold text-purple-700 mb-1">PROJECTS</div>
            <button className="text-purple-700 text-sm flex items-center gap-1" onClick={addProject}>
              <FaPlus /> Add
            </button>
          </div>
          <div className="flex flex-col gap-3">
            {resume.projects.map((proj, idx) => (
              <div key={idx} className="rounded-lg border border-gray-200 bg-gray-50 p-4 relative">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input
                    className="border-b border-purple-200 py-1 px-2 outline-none"
                    placeholder="Project Name"
                    value={proj.name}
                    onChange={e => handleProj(idx, "name", e.target.value)}
                  />
                  <input
                    className="border-b border-purple-200 py-1 px-2 outline-none"
                    placeholder="Technologies (comma-separated)"
                    value={proj.tech}
                    onChange={e => handleProj(idx, "tech", e.target.value)}
                  />
                  <input
                    className="col-span-2 border-b border-purple-100 py-1 px-2 outline-none"
                    placeholder="Link (optional)"
                    value={proj.link}
                    onChange={e => handleProj(idx, "link", e.target.value)}
                  />
                </div>
                <textarea
                  className="w-full mt-2 border border-purple-100 rounded p-2 bg-white text-sm focus:ring"
                  placeholder="Short project description, achievements…"
                  value={proj.description}
                  onChange={e => handleProj(idx, "description", e.target.value)}
                />
                {resume.projects.length > 1 && (
                  <button
                    className="absolute top-2 right-2 text-gray-400 hover:text-red-500"
                    onClick={() => removeProject(idx)}
                  >
                    <FaTrash />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// --- Plain text renderer for export/download ---
function renderPlainText(resume) {
  let text = "";
  text += `${resume.fullName || ""}\n${resume.emailPhone || ""}\n${resume.linkedin || ""}\n${resume.github || ""}\n\n`;
  if (resume.summary) text += `SUMMARY\n${resume.summary}\n\n`;
  if (resume.education && resume.education.length) {
    text += "EDUCATION\n";
    resume.education.forEach(e =>
      text += `${e.degree || ""}, ${e.school || ""}, ${e.location || ""}, ${e.date || ""}\n${e.details || ""}\n`
    );
    text += "\n";
  }
  if (resume.experience && resume.experience.length) {
    text += "EMPLOYMENT EXPERIENCE\n";
    resume.experience.forEach(e =>
      text += `${e.title || ""}, ${e.company || ""}, ${e.location || ""}, ${e.date || ""}\n${e.details || ""}\n`
    );
    text += "\n";
  }
  if (resume.projects && resume.projects.length) {
    text += "PROJECTS\n";
    resume.projects.forEach(p =>
      text += `${p.name || ""}${p.tech ? ` [${p.tech}]` : ""}${p.link ? ` (${p.link})` : ""}\n${p.description || ""}\n`
    );
    text += "\n";
  }
  return text;
}
