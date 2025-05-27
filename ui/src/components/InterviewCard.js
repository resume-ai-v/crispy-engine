export default function InterviewCard({ title, type, interviewer, goal, format, skills }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow hover:shadow-md transition">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-purple-700">{title}</h2>
        <span className="text-sm bg-purple-100 text-purple-700 px-3 py-1 rounded">{type}</span>
      </div>
      <p className="text-sm text-gray-500 mb-1">AI Interviewer: {interviewer}</p>
      <p className="mt-2 text-gray-700"><strong>Goal:</strong> {goal}</p>
      <p className="text-gray-700 mt-2"><strong>Format:</strong> {format}</p>
      <div className="mt-2">
        <strong className="block mb-1 text-gray-700">Skills Tested:</strong>
        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
          {skills.map((skill, i) => <li key={i}>{skill}</li>)}
        </ul>
      </div>
      <button className="mt-4 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded">
        Join Now
      </button>
    </div>
  );
}
