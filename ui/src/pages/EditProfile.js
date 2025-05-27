// src/pages/EditProfile.js
import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import { useNavigate } from 'react-router-dom';

export default function EditProfile() {
  const navigate = useNavigate();
  const storedUser = JSON.parse(localStorage.getItem('user')) || {};
  const [firstName, setFirstName] = useState(storedUser.firstName || '');
  const [lastName, setLastName] = useState(storedUser.lastName || '');
  const [email, setEmail] = useState(storedUser.email || '');

  const handleSave = (e) => {
    e.preventDefault();

    const updatedUser = { firstName, lastName, email };
    localStorage.setItem('user', JSON.stringify(updatedUser));
    localStorage.setItem('userFullName', `${firstName} ${lastName}`);
    localStorage.setItem('loggedInUser', email);

    navigate('/profile');
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar active="" />
      <main className="flex-1 p-8 overflow-y-auto">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">✏️ Edit Profile</h1>

        <form onSubmit={handleSave} className="space-y-4 max-w-md">
          <input
            type="text"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            placeholder="First Name"
            required
            className="w-full border px-4 py-2 rounded"
          />
          <input
            type="text"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            placeholder="Last Name"
            required
            className="w-full border px-4 py-2 rounded"
          />
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            required
            className="w-full border px-4 py-2 rounded"
          />

          <button
            type="submit"
            className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
          >
            Save Changes
          </button>
        </form>
      </main>
    </div>
  );
}
