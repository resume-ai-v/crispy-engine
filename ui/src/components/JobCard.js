// src/components/JobCard.js
export default function JobCard({ title, company, location, salary, match, posted, onClick }) {
  return (
    <div
      onClick={onClick}
      className="bg-white p-5 rounded-lg shadow hover:shadow-md transition cursor-pointer"
    >
      <h2 className="text-lg font-semibold text-purple-700">{title}</h2>
      <p className="text-sm text-gray-600">{company} • {location}</p>
      <p className="text-sm text-gray-600 mt-1">💰 {salary}</p>
      <p className="text-sm text-green-600">{match}</p>
      <p className="text-xs text-gray-500">{posted}</p>

      <button
        onClick={(e) => {
          e.stopPropagation(); // Prevent parent onClick
          onClick();
        }}
        className="mt-4 px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
      >
        View Details
      </button>
    </div>
  );
}
