import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import UserDropdown from "../components/UserDropdown";
import AvatarPlayer from "../components/AvatarPlayer";
import { evaluateAnswer as evaluateAnswerAPI } from "../utils/api";

export default function AIInterviewPractice() {
  const [questions, setQuestions] = useState([]);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(false);
  const [avatarVideoUrl, setAvatarVideoUrl] = useState("");
  const [avatarAudioUrl, setAvatarAudioUrl] = useState("");

  const resumeText = localStorage.getItem("resumeText") || "";

  const startAvatarInterview = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/start-interview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume: resumeText,
          jd: "Generic",
          round: "HR",
        }),
      });

      const data = await res.json();

      setQuestions([data.question]);
      setSelectedQuestion(data.question);
      setCurrentAnswer(data.answer || "");
      setAvatarVideoUrl(data.video_url);
      setAvatarAudioUrl(data.audio_url);
    } catch (err) {
      console.error("Avatar Interview Error:", err);
      alert("❌ Failed to start AI Avatar Interview.");
    } finally {
      setLoading(false);
    }
  };

  const evaluateAnswer = async () => {
    if (!selectedQuestion || !currentAnswer) return;

    setLoading(true);
    try {
      const data = await evaluateAnswerAPI(selectedQuestion, currentAnswer);
      setFeedback(data.feedback || "No feedback returned.");
    } catch (err) {
      console.error("Error evaluating answer:", err);
      alert("❌ Something went wrong during evaluation.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    startAvatarInterview(); // Fetch first question
  }, []);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar active="interview" />

      <main className="flex-1 overflow-y-auto p-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">AI Interview Practice</h1>
            <p className="text-sm text-gray-500">AI-generated mock interviews tailored to your resume</p>
          </div>
          <UserDropdown />
        </div>

        <div className="grid grid-cols-12 gap-8">
          {/* Left: Questions List */}
          <div className="col-span-4 bg-white rounded-lg shadow p-5">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Interview Questions</h2>
            {questions.map((q, index) => (
              <div
                key={index}
                onClick={() => {
                  setSelectedQuestion(q);
                  setCurrentAnswer("");
                  setFeedback("");
                }}
                className={`border rounded px-4 py-2 cursor-pointer mb-3 text-sm font-medium ${
                  selectedQuestion === q
                    ? "bg-purple-100 border-purple-500 text-purple-800"
                    : "hover:bg-gray-100 text-gray-700"
                }`}
              >
                {q}
              </div>
            ))}
          </div>

          {/* Right: Answer Panel */}
          <div className="col-span-8 bg-white rounded-lg shadow p-6">
            {selectedQuestion ? (
              <>
                <h3 className="text-md font-semibold text-gray-700 mb-2">{selectedQuestion}</h3>
                <textarea
                  rows={6}
                  value={currentAnswer}
                  onChange={(e) => setCurrentAnswer(e.target.value)}
                  className="w-full border border-gray-300 rounded px-4 py-2 mb-4 focus:outline-none focus:ring focus:border-purple-500"
                  placeholder="Type your response here..."
                />

                <button
                  onClick={evaluateAnswer}
                  disabled={loading || !currentAnswer}
                  className="bg-purple-600 text-white px-5 py-2 rounded hover:bg-purple-700 transition"
                >
                  Get Feedback
                </button>

                {feedback && (
                  <div className="mt-6 border border-gray-200 bg-gray-50 p-4 rounded">
                    <h4 className="font-semibold text-gray-800 mb-2">🔍 AI Feedback:</h4>
                    <p className="text-sm text-gray-700 whitespace-pre-line">{feedback}</p>
                  </div>
                )}

                <AvatarPlayer videoUrl={avatarVideoUrl} audioUrl={avatarAudioUrl} />
              </>
            ) : (
              <p className="text-gray-600">Select a question to begin your AI mock interview.</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
