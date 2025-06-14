import React, { useState } from "react";
import UserDropdown from "../components/UserDropdown";
import AvatarPlayer from "../components/AvatarPlayer";
import { evaluateAnswer as evaluateAnswerAPI, API_BASE, withAuth } from "../utils/api"; // <-- import withAuth

// --- Define Interview Rounds ---
const INTERVIEW_ROUNDS = [
  {
    id: "coding",
    title: "Coding Round",
    type: "Online",
    interviewer: "Jhon",
    avatarPhoto: "/avatars/coding_jhon.png",
    goal: "Assess data structures and algorithms proficiency.",
    format: "2–3 coding questions on platforms like HackerRank, Codility, or CodeSignal.",
    skills: [
      "Arrays, Strings, Hashmaps",
      "Trees, Graphs",
      "Dynamic Programming",
      "Greedy, Backtracking",
    ],
    avatarRound: "coding",
  },
  {
    id: "system-design",
    title: "System Design Round",
    type: "Offline",
    interviewer: "Samantha",
    avatarPhoto: "/avatars/system_samantha.png",
    goal: "Test ability to design scalable systems.",
    format: "Low-level & High-level design: Classes, APIs, architecture, tradeoffs.",
    skills: [
      "Class & API relationships (LLD)",
      "Architecture, caching, scaling (HLD)",
      "Trade-offs, modular design",
    ],
    avatarRound: "system-design",
  },
  {
    id: "hr",
    title: "Behavioral / HR Round",
    type: "Online",
    interviewer: "Ben",
    avatarPhoto: "/avatars/hr_ben.png",
    goal: "Culture fit and communication.",
    format: "STAR method preferred (Situation, Task, Action, Result).",
    skills: [
      "Why this company?",
      "Conflict resolution",
      "Leadership, teamwork",
      "Past project discussions",
    ],
    avatarRound: "hr",
  },
];

export default function AIInterviewPractice() {
  const [selectedRound, setSelectedRound] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState("");
  const [avatarVideoUrl, setAvatarVideoUrl] = useState("");
  const [avatarAudioUrl, setAvatarAudioUrl] = useState("");
  const [loadingRoundId, setLoadingRoundId] = useState(null);
  const [feedbackLoading, setFeedbackLoading] = useState(false);

  // Try resume from localStorage (as uploaded or pasted in AI Resume)
  const resumeText = localStorage.getItem("resumeText") || "";

  // --- Start AI Avatar Interview (calls backend endpoint) ---
  const startAvatarInterview = async (round) => {
    setLoadingRoundId(round.id);
    setFeedback("");
    setAnswer("");
    setQuestion("");
    setAvatarVideoUrl("");
    setAvatarAudioUrl("");
    try {
      const res = await fetch(`${API_BASE}/start-interview`, {
        method: "POST",
        headers: withAuth({ "Content-Type": "application/json" }), // <-- Use withAuth here!
        body: JSON.stringify({
          resume: resumeText,
          jd: "Generic",
          round: round.avatarRound,
        }),
      });
      if (!res.ok) throw new Error("Failed to start interview session");
      const data = await res.json();
      setSelectedRound(round);
      setQuestion(data.question || "");
      setAnswer(""); // Always start with empty answer
      setAvatarVideoUrl(data.video_url || "");
      setAvatarAudioUrl(data.audio_url || "");
    } catch (err) {
      alert("❌ Failed to start AI Avatar Interview. Please try again.");
      setSelectedRound(null);
    } finally {
      setLoadingRoundId(null);
    }
  };

  // --- Get AI Feedback for answer ---
  const evaluateAnswer = async () => {
    if (!question || !answer) return;
    setFeedbackLoading(true);
    try {
      const data = await evaluateAnswerAPI(answer, question);
      setFeedback(data.feedback || "No feedback returned.");
    } catch (err) {
      alert("❌ Something went wrong during evaluation.");
    } finally {
      setFeedbackLoading(false);
    }
  };

  // --- UI ---
  return (
    <main className="flex-1 overflow-y-auto p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">AI Interview Practice</h1>
          <p className="text-sm text-gray-500">AI-generated mock interviews tailored to your resume</p>
        </div>
        <UserDropdown />
      </div>

      {/* Show Interview Rounds as cards if not in a round */}
      {!selectedRound && (
        <div>
          <div className="text-lg font-semibold text-gray-700 mb-4">
            Recommended AI Interviews
          </div>
          <div className="grid gap-7">
            {INTERVIEW_ROUNDS.map((round) => (
              <div
                key={round.id}
                className="bg-white p-6 rounded-xl shadow hover:shadow-md flex flex-col sm:flex-row sm:items-center gap-7 transition"
              >
                <div className="flex-shrink-0">
                  <img
                    src={round.avatarPhoto}
                    alt={round.interviewer}
                    className="w-20 h-20 rounded-full object-cover border-2 border-purple-200"
                  />
                </div>
                <div className="flex-1">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
                    <h2 className="text-xl font-bold text-purple-700">{round.title}</h2>
                    <span className="text-xs bg-purple-100 text-purple-700 px-3 py-1 rounded-full">{round.type}</span>
                    <span className="text-xs text-gray-500">| AI Interviewer: {round.interviewer}</span>
                  </div>
                  <div className="mb-1">
                    <span className="font-semibold text-gray-700">Goal:</span>{" "}
                    <span className="text-gray-700">{round.goal}</span>
                  </div>
                  <div className="mb-1">
                    <span className="font-semibold text-gray-700">Format:</span>{" "}
                    <span className="text-gray-700">{round.format}</span>
                  </div>
                  <div>
                    <span className="font-semibold text-gray-700">Skills Tested:</span>
                    <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 mt-1">
                      {round.skills.map((skill, i) => (
                        <li key={i}>{skill}</li>
                      ))}
                    </ul>
                  </div>
                </div>
                <button
                  className="mt-4 sm:mt-0 bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded shadow text-base font-semibold"
                  onClick={() => startAvatarInterview(round)}
                  disabled={loadingRoundId === round.id}
                >
                  {loadingRoundId === round.id ? "Loading..." : "Join Now"}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Show Q&A if in a round */}
      {selectedRound && (
        <div className="max-w-3xl mx-auto mt-10 bg-white rounded-xl shadow p-8">
          <div className="mb-4 flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold text-purple-700">{selectedRound.title}</h2>
              <div className="text-xs text-gray-500">AI Interviewer: {selectedRound.interviewer}</div>
            </div>
            <button
              className="text-gray-500 hover:text-purple-700 text-sm"
              onClick={() => {
                setSelectedRound(null);
                setFeedback("");
                setAnswer("");
                setQuestion("");
                setAvatarVideoUrl("");
                setAvatarAudioUrl("");
              }}
            >
              ← Back to Rounds
            </button>
          </div>

          {question && (
            <>
              <div className="text-lg font-semibold text-gray-700 mb-2">{question}</div>
              <textarea
                rows={5}
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                className="w-full border border-gray-300 rounded px-4 py-2 mb-4 focus:outline-none focus:ring focus:border-purple-500"
                placeholder="Type your response here..."
              />
              <button
                onClick={evaluateAnswer}
                disabled={feedbackLoading || !answer}
                className="bg-purple-600 text-white px-5 py-2 rounded hover:bg-purple-700 transition"
              >
                {feedbackLoading ? "Loading..." : "Get Feedback"}
              </button>
            </>
          )}

          {feedback && (
            <div className="mt-6 border border-gray-200 bg-gray-50 p-4 rounded">
              <h4 className="font-semibold text-gray-800 mb-2">🔍 AI Feedback:</h4>
              <p className="text-sm text-gray-700 whitespace-pre-line">{feedback}</p>
            </div>
          )}

          {/* Avatar video/audio loads as soon as URLs are available */}
          <AvatarPlayer videoUrl={avatarVideoUrl} audioUrl={avatarAudioUrl} />
        </div>
      )}
    </main>
  );
}
