export const API_BASE = "https://crispy-engine-nx6e.onrender.com/api";

// Helper: get session-token from localStorage
const getToken = () => localStorage.getItem("token");

// Attach Authorization header if token present (MVP session token)
const withAuth = (headers = {}) => {
  const token = getToken();
  return token ? { ...headers, Authorization: token } : headers;
};

// Signup (new user)
export const signup = async (first_name, last_name, email, password) => {
  const res = await fetch(`${API_BASE}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ first_name, last_name, email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Signup failed");
  if (data.token) localStorage.setItem("token", data.token); // Save MVP session token!
  return data;
};

// Login
export const login = async (email, password) => {
  const res = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Login failed");
  if (data.token) localStorage.setItem("token", data.token);
  return data;
};

// Suggest endpoints (no auth required!)
export const suggestSkills = async (query) => {
  const res = await fetch(`${API_BASE}/suggest/skills?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error("Failed to fetch skills");
  return (await res.json()).options || [];
};
export const suggestRoles = async (query) => {
  const res = await fetch(`${API_BASE}/suggest/roles?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error("Failed to fetch roles");
  return (await res.json()).options || [];
};
export const suggestCities = async (query) => {
  const res = await fetch(`${API_BASE}/suggest/cities?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error("Failed to fetch cities");
  return (await res.json()).options || [];
};

// Onboarding (AUTH REQUIRED!)
export const submitOnboarding = async (data) => {
  const res = await fetch(`${API_BASE}/onboarding`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify(data),
  });
  const result = await res.json();
  if (!res.ok) throw new Error(result.detail || "Onboarding submission failed");
  return result;
};

export const getOnboarding = async () => {
  const res = await fetch(`${API_BASE}/onboarding`, {
    method: "GET",
    headers: withAuth(),
  });
  if (!res.ok) return {};
  return res.json();
};
