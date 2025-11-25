import React, { useState } from 'react';
import ResumeUpload from './components/ResumeUpload';
import CareerPaths from './components/CareerPaths';
import { Compass } from 'lucide-react';

function App() {
  const [parsedData, setParsedData] = useState(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex items-center">
          <Compass className="w-8 h-8 text-blue-600 mr-3" />
          <h1 className="text-2xl font-bold text-gray-900">Career Navigator</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {!parsedData ? (
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="text-center mb-10">
              <h2 className="text-4xl font-extrabold text-gray-900 mb-4">
                Discover Your Next Career Move
              </h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Upload your resume to get AI-powered career path recommendations tailored to your skills and experience.
              </p>
            </div>
            <ResumeUpload onUploadSuccess={setParsedData} />
          </div>
        ) : (
          <div className="animate-fade-in">
            <div className="bg-blue-600 text-white p-6 rounded-lg shadow-lg mb-8">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-bold">Welcome, {parsedData.full_name}</h2>
                  <p className="opacity-90 mt-1">{parsedData.current_role} • {parsedData.years_total_experience} Years Experience</p>
                </div>
                <button 
                  onClick={() => setParsedData(null)}
                  className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded transition-colors"
                >
                  Upload New Resume
                </button>
              </div>
              <div className="mt-6">
                <p className="text-sm font-medium opacity-75 mb-2">Detected Skills:</p>
                <div className="flex flex-wrap gap-2">
                  {parsedData.skills.map((skill, i) => (
                    <span key={i} className="bg-white/20 px-2 py-1 rounded text-sm">
                      {skill.name}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            
            <CareerPaths parsedData={parsedData} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
