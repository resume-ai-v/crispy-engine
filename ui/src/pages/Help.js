// src/pages/Help.js
import React from 'react';
import Sidebar from '../components/Sidebar';

export default function Help() {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar active="" />
      <main className="flex-1 p-8 overflow-y-auto">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">❓ Help</h1>
        <p className="text-gray-700">
          If you need assistance using LaunchHire, please reach out to support@example.com.
        </p>
      </main>
    </div>
  );
}
