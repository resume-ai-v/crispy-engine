// src/utils/timeAgo.js
export function timeAgo(dateString) {
  const diff = Math.floor((new Date() - new Date(dateString)) / 1000);

  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}min ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}hr ago`;
  if (diff < 2592000) return `${Math.floor(diff / 86400)} days ago`;
  return new Date(dateString).toLocaleDateString();
}
