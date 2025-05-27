// src/pages/Profile.js
import React from 'react';
import Sidebar from '../components/Sidebar';

export default function Profile() {
  const user = JSON.parse(localStorage.getItem('user'));

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar active="" />
      <main className="flex-1 p-8 overflow-y-auto">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">👤 Profile</h1>
        {user ? (
          <div className="space-y-2 text-gray-700">
            <p><strong>First Name:</strong> {user.firstName}</p>
            <p><strong>Last Name:</strong> {user.lastName}</p>
            <p><strong>Email:</strong> {user.email}</p>
          </div>
        ) : (
          <p className="text-red-500">No user data found.</p>
        )}
      </main>
    </div>
  );
}
