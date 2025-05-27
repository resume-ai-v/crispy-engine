import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function UserDropdown() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const fullName = localStorage.getItem('userFullName') || 'Guest';

  const handleLogout = () => {
    localStorage.clear();
    navigate('/');
  };

  return (
    <div className="relative inline-block text-left">
      <div
        onClick={() => setOpen(!open)}
        className="cursor-pointer text-sm text-gray-600 hover:text-gray-800"
      >
        {fullName} <span className="ml-1">▼</span>
      </div>

      {open && (
        <div className="absolute right-0 mt-2 w-40 bg-white shadow-lg rounded-md z-10">
          <ul className="py-1 text-sm text-gray-700">
            <li>
              <button
                onClick={() => alert('Profile clicked')}
                className="w-full text-left px-4 py-2 hover:bg-gray-100"
              >
                Profile
              </button>
            </li>
            <li>
              <button
                onClick={() => alert('Edit clicked')}
                className="w-full text-left px-4 py-2 hover:bg-gray-100"
              >
                Edit
              </button>
            </li>
            <li>
              <button
                onClick={handleLogout}
                className="w-full text-left px-4 py-2 text-red-500 hover:bg-red-100"
              >
                Logout
              </button>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}
