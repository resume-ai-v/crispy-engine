import React from 'react';
import Sidebar from '../components/Sidebar';
import InterviewCard from '../components/InterviewCard';

const interviewRounds = [
  {
    title: "Coding Round",
    type: "Online",
    interviewer: "Jhon",
    goal: "Assess data structures and algorithms proficiency.",
    format: "2–3 coding questions on HackerRank or CodeSignal.",
    skills: ["Arrays", "Strings", "Hashmap", "Graphs", "DP", "Greedy"],
  },
  {
    title: "System Design Round",
    type: "Offline",
    interviewer: "Samantha",
    goal: "Test ability to design scalable systems.",
    format: "LLD: Classes & APIs, HLD: Architecture & scaling.",
    skills: ["Design Thinking", "APIs", "Load Balancing", "Modularity"],
  },
  {
    title: "Behavioral / HR Round",
    type: "Online",
    interviewer: "Ben",
    goal: "Assess culture fit and communication.",
    format: "STAR method: Situation, Task, Action, Result.",
    skills: ["Leadership", "Conflict Resolution", "Teamwork"],
  },
];

export default function AIInterviewPractice() {
  const userName = localStorage.getItem("userFullName") || "Guest";

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar active="interview" />

      <main className="flex-1 p-8 overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Recommended AI Interviews</h1>
          <div className="relative group">
            <button className="text-sm font-medium text-gray-700 group-hover:text-purple-600">
              {userName} <span className="ml-1">▼</span>
            </button>
            <div className="absolute right-0 mt-2 w-40 bg-white rounded-md shadow-lg hidden group-hover:block z-10">
              <a href="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                Profile
              </a>
              <a href="/settings" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                Settings
              </a>
              <a href="/help" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                Help
              </a>
              <a href="/logout" className="block px-4 py-2 text-sm text-red-600 hover:bg-gray-100">
                Logout
              </a>
            </div>
          </div>
        </div>

        <div className="grid gap-6">
          {interviewRounds.map((round, index) => (
            <InterviewCard key={index} {...round} />
          ))}
        </div>
      </main>
    </div>
  );
}
