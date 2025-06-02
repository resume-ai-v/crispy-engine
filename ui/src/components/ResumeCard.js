import React from "react";

// Helper: extract sections (very simple parser)
function parseResume(text) {
  const sections = {};
  let currentSection = "SUMMARY";
  let buffer = [];
  text.split("\n").forEach((line) => {
    // Section headings: look for all-caps or standard sections
    const headingMatch = line.match(/^([A-Z][A-Z\s]+|SUMMARY|EDUCATION|EXPERIENCE|SKILLS|PROJECTS|TECHNICAL)/);
    if (headingMatch && line.trim().length < 35) {
      if (buffer.length) sections[currentSection] = buffer.join("\n").trim();
      currentSection = headingMatch[1].trim();
      buffer = [];
    } else {
      buffer.push(line);
    }
  });
  if (buffer.length) sections[currentSection] = buffer.join("\n").trim();
  return sections;
}

export default function ResumeCard({ resumeText }) {
  if (!resumeText) {
    return (
      <div className="bg-gray-50 p-10 rounded-xl text-center text-gray-400">
        <div className="mb-2 font-bold text-xl">AI Resume Preview</div>
        <div className="text-sm">Your tailored resume will appear here.</div>
      </div>
    );
  }

  const sections = parseResume(resumeText);

  return (
    <div className="bg-white p-8 rounded-xl shadow w-full text-gray-800 leading-relaxed">
      {/* Name/Header */}
      {sections.NAME && (
        <div className="mb-2">
          <h2 className="text-2xl font-bold">{sections.NAME}</h2>
        </div>
      )}
      {/* Contact */}
      {sections.CONTACT && (
        <div className="mb-2 text-sm text-gray-600">{sections.CONTACT}</div>
      )}

      {/* Main sections */}
      {Object.entries(sections).map(([heading, content]) => {
        if (["NAME", "CONTACT"].includes(heading)) return null;
        return (
          <div className="mb-6" key={heading}>
            <h3 className="text-lg font-bold text-purple-700 mb-2">{heading.replace(/_/g, " ")}</h3>
            <div className="text-sm whitespace-pre-line">
              {content}
            </div>
          </div>
        );
      })}
    </div>
  );
}
