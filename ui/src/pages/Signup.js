import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Signup() {
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');

  // 🚨 DEBUG: Let us know which Signup.js is running!
  const handleSignup = async (e) => {
    e.preventDefault();
    alert("You are running the **REAL** Signup.js from ui/src/pages/Signup.js!");

    if (!email.includes('@')) {
      setError('⚠️ Invalid email address');
      return;
    }

    if (password.length < 4) {
      setError('⚠️ Password must be at least 4 characters');
      return;
    }

    if (password !== confirmPassword) {
      setError('⚠️ Passwords do not match');
      return;
    }

    try {
      const full_name = `${firstName} ${lastName}`;
      // 🚨 GUARANTEED: Always use Render backend, never localhost!
      const response = await fetch(
        "https://crispy-engine-1.onrender.com/api/signup",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ full_name, email, password }),
        }
      );
      const data = await response.json();

      if (!response.ok) {
        setError(`❌ ${data.detail || "Signup failed"}`);
        return;
      }

      alert("Signup request went to the REAL backend!");
      localStorage.setItem('userFullName', full_name);
      localStorage.setItem('loggedInUser', email);
      navigate('/api/onboarding');
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

        <form onSubmit={handleSignup} className="space-y-4">
          <input type="text" placeholder="First Name" value={firstName} onChange={(e) => setFirstName(e.target.value)} required className="w-full border px-4 py-2 rounded" />
          <input type="text" placeholder="Last Name" value={lastName} onChange={(e) => setLastName(e.target.value)} required className="w-full border px-4 py-2 rounded" />
          <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full border px-4 py-2 rounded" />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full border px-4 py-2 rounded" />
          <input type="password" placeholder="Confirm Password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required className="w-full border px-4 py-2 rounded" />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700">Sign Up</button>
        </form>

        <p className="text-center text-sm mt-4">
          Already have an account?{' '}
          <a href="/" className="text-purple-600 font-medium hover:underline">Log In</a>
        </p>
      </div>
    </div>
  );
}
