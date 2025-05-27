export default function ResumeCard() {
  return (
    <div className="bg-white p-6 rounded-lg shadow w-full max-w-3xl">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold">ROHITH R KRISHNAN</h2>
          <p className="text-sm text-gray-600">Software Engineer</p>
          <p className="text-sm text-gray-600">
            (+91) 8086112313 • rohit.krishna1521@gmail.com • www.rohitkrishna.com
          </p>
        </div>
        <button className="border px-4 py-1 rounded text-sm">Edit</button>
      </div>

      {/* Skills */}
      <div className="mt-6">
        <h3 className="font-semibold mb-2">SKILLS</h3>
        <ul className="text-sm text-gray-700 columns-2 space-y-1">
          <li>Rapid Prototyping</li>
          <li>Storyboarding</li>
          <li>Design Research</li>
          <li>Interaction Design</li>
          <li>Wireframing</li>
          <li>UI Designing</li>
          <li>After Effects</li>
          <li>Framer</li>
          <li>Protopie</li>
          <li>Web (HTML, CSS, JS)</li>
          <li>Android (Flutter, Kotlin)</li>
        </ul>
      </div>

      {/* Experiences */}
      <div className="mt-6">
        <h3 className="font-semibold mb-2">EXPERIENCES</h3>
        <p className="font-semibold text-sm">Product Designer | Disney+Hotstar</p>
        <p className="text-xs text-gray-500">Bangalore, IN | Sep 2021 – Current</p>
        <p className="text-sm text-gray-700 mb-3">
          Working on subscription and ad experiences across mobile, tablet, and TV platforms.
        </p>

        <p className="font-semibold text-sm">Product Designer | Dunzo</p>
        <p className="text-xs text-gray-500">Bangalore, IN | Jan 2020 – Sep 2021</p>
        <p className="text-sm text-gray-700">
          Designed end-to-end features including Dunzo Daily, payment experience, and design systems.
        </p>
      </div>

      {/* Education */}
      <div className="mt-6">
        <h3 className="font-semibold mb-2">EDUCATION</h3>
        <p className="text-sm text-gray-800">B.Tech in Electronics and Communication</p>
        <p className="text-xs text-gray-500">Amrita Vishwa Vidyapeetham, Kerala (2016–2020)</p>
      </div>
    </div>
  );
}
