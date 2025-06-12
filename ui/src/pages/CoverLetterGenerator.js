// src/pages/CoverLetterGenerator.js

import React, { useState, useEffect } from 'react';
import { generateCoverLetter as generateCoverLetterAPI, getOnboarding } from '../utils/api';

const CoverLetterGenerator = () => {
    const [resume, setResume] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    const [userName, setUserName] = useState('');
    const [hiringManager, setHiringManager] = useState('');
    const [companyName, setCompanyName] = useState('');
    const [industry, setIndustry] = useState('');
    const [generatedLetter, setGeneratedLetter] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    // --- Load name & resume from onboarding/localStorage ---
    useEffect(() => {
        async function load() {
            try {
                // Try onboarding profile first (reliable for signed-in users)
                const data = await getOnboarding();
                setUserName(
                    data.full_name ||
                    data.user_name ||
                    data.first_name + " " + (data.last_name || "") ||
                    ""
                );
                setResume(
                    data.resume_text ||
                    data.resume ||
                    localStorage.getItem("resumeText") ||
                    ""
                );
            } catch {
                // fallback to localStorage if onboarding fails
                setResume(localStorage.getItem("resumeText") || "");
            }
        }
        load();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!resume || !jobDescription || !userName || !companyName) {
            setError('Please fill in all required fields: Your Resume, Job Description, Your Name, and Company Name.');
            return;
        }
        setError('');
        setIsLoading(true);
        setGeneratedLetter('');
        try {
            const response = await generateCoverLetterAPI({
                resume_text: resume,
                job_description: jobDescription,
                user_name: userName,
                hiring_manager: hiringManager,
                company_name: companyName,
                industry: industry,
            });
            setGeneratedLetter(response.cover_letter || "No cover letter returned.");
        } catch (err) {
            setError(err.message || 'Failed to generate cover letter. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="p-4 md:p-8 w-full min-h-screen bg-gray-50">
            <h1 className="text-3xl font-bold mb-2">AI-Powered Cover Letter Generator</h1>
            <p className="text-gray-600 mb-8">Create a compelling cover letter tailored to any job in seconds.</p>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Left Side: Inputs */}
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="resume" className="block text-sm font-medium text-gray-700 mb-1">Paste Your Resume</label>
                            <textarea id="resume" value={resume} onChange={(e) => setResume(e.target.value)} rows={10} className="w-full p-2 border border-gray-300 rounded-md shadow-sm" placeholder="Paste your full resume text here..." required />
                        </div>
                        <div>
                            <label htmlFor="jobDescription" className="block text-sm font-medium text-gray-700 mb-1">Paste Job Description</label>
                            <textarea id="jobDescription" value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} rows={10} className="w-full p-2 border border-gray-300 rounded-md shadow-sm" placeholder="Paste the job description here..." required />
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="userName" className="block text-sm font-medium text-gray-700 mb-1">Your Name</label>
                                <input type="text" id="userName" value={userName} onChange={(e) => setUserName(e.target.value)} className="w-full p-2 border border-gray-300 rounded-md shadow-sm" required />
                            </div>
                            <div>
                                <label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
                                <input type="text" id="companyName" value={companyName} onChange={(e) => setCompanyName(e.target.value)} className="w-full p-2 border border-gray-300 rounded-md shadow-sm" required />
                            </div>
                            <div>
                                <label htmlFor="hiringManager" className="block text-sm font-medium text-gray-700 mb-1">Hiring Manager's Name <span className="text-gray-400">(optional)</span></label>
                                <input type="text" id="hiringManager" value={hiringManager} onChange={(e) => setHiringManager(e.target.value)} className="w-full p-2 border border-gray-300 rounded-md shadow-sm" />
                            </div>
                            <div>
                                <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-1">Company's Industry <span className="text-gray-400">(optional)</span></label>
                                <input type="text" id="industry" value={industry} onChange={(e) => setIndustry(e.target.value)} className="w-full p-2 border border-gray-300 rounded-md shadow-sm" />
                            </div>
                        </div>
                        <button type="submit" disabled={isLoading} className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:bg-purple-300 transition-colors">
                            {isLoading ? 'Generating...' : 'Generate Cover Letter'}
                        </button>
                    </div>

                    {/* Right Side: Output */}
                    <div className="bg-white p-6 border border-gray-200 rounded-md shadow-sm">
                        <h2 className="text-xl font-semibold mb-4">Generated Cover Letter</h2>
                        {isLoading && <p className="text-gray-500">Please wait, the AI is writing your letter...</p>}
                        {error && <div className="text-red-500 bg-red-50 p-4 rounded-md">{error}</div>}
                        <div className="prose prose-sm max-w-none whitespace-pre-wrap text-gray-800">
                            {generatedLetter || (!isLoading && <p className="text-gray-400">Your generated cover letter will appear here.</p>)}
                        </div>
                    </div>
                </div>
            </form>
        </div>
    );
};

export default CoverLetterGenerator;
