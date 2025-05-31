import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      setError('⚠️ Please enter both email and password.');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(`❌ ${data.detail || "Login failed"}`);
        return;
      }

      localStorage.setItem('loggedInUser', email);
      localStorage.setItem('userFullName', data.full_name || email);
      setError('');
      navigate('/onboarding');
    } catch (err) {
      setError('❌ Server error. Please try again.');
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6 text-purple-600">
          Launch<span className="text-gray-900">Hire</span>
        </h1>

        <form onSubmit={handleLogin} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full border px-4 py-2 rounded"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full border px-4 py-2 rounded"
          />

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button
            type="submit"
            className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700"
          >
            Log In
          </button>
        </form>

        <p className="text-center text-sm mt-4">
          Don’t have an account?{' '}
          <a href="/signup" className="text-purple-600 font-medium hover:underline">
            Sign Up
          </a>
        </p>
      </div>
    </div>
  );
}
