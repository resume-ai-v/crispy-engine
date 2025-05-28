import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import UserDropdown from "../components/UserDropdown";
import { fetchInterviewQuestions, evaluateAnswer as evaluateAnswerAPI } from "../utils/api";

export default function AIInterviewPractice() {
  const [questions, setQuestions] = useState([]);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(false);

  const resumeText = localStorage.getItem("resumeText") || "";

  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const data = await fetchInterviewQuestions(resumeText);
      if (Array.isArray(data.questions)) {
        setQuestions(data.questions);
      } else {
        alert("❌ Failed to fetch questions.");
      }
    } catch (err) {
      console.error("Error fetching questions:", err);
      alert("❌ Something went wrong while fetching questions.");
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
    fetchQuestions();
  }, []);

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar active="interview" />
      <main className="flex-1 p-8 overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">AI Interview Practice</h1>
          <UserDropdown />
        </div>

        {loading && <p className="text-gray-600">⏳ Loading...</p>}

        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-1">
            <h2 className="text-lg font-semibold mb-2 text-gray-700">Interview Questions</h2>
            <ul className="space-y-2">
              {questions.map((q, index) => (
                <li
                  key={index}
                  onClick={() => {
                    setSelectedQuestion(q);
                    setCurrentAnswer("");
                    setFeedback("");
                  }}
                  className={`cursor-pointer p-3 rounded border ${
                    selectedQuestion === q
                      ? "bg-purple-100 border-purple-600"
                      : "hover:bg-gray-100"
                  }`}
                >
                  {q}
                </li>
              ))}
            </ul>
          </div>

          <div className="col-span-2 bg-white p-6 rounded shadow">
            {selectedQuestion ? (
              <>
                <h3 className="text-md font-medium text-gray-700 mb-2">{selectedQuestion}</h3>
                <textarea
                  rows={6}
                  value={currentAnswer}
                  onChange={(e) => setCurrentAnswer(e.target.value)}
                  className="w-full border px-3 py-2 rounded mb-4"
                  placeholder="Type your answer here..."
                ></textarea>
                <button
                  onClick={evaluateAnswer}
                  disabled={loading || !currentAnswer}
                  className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
                >
                  Get Feedback
                </button>

                {feedback && (
                  <div className="mt-4 bg-gray-100 p-4 rounded border">
                    <h4 className="font-medium text-gray-700 mb-1">🔍 AI Feedback:</h4>
                    <p className="text-sm text-gray-800">{feedback}</p>
                  </div>
                )}
              </>
            ) : (
              <p className="text-gray-600">🧠 Select a question to practice...</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
