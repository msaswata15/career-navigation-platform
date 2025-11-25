import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ArrowRight, TrendingUp, Clock, Award, AlertCircle } from 'lucide-react';

const CareerPaths = ({ parsedData }) => {
  const [paths, setPaths] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [targetRole, setTargetRole] = useState('');

  const fetchCareerPaths = async () => {
    setLoading(true);
    setError(null);

    try {
      const payload = {
        current_role: parsedData.current_role,
        user_skills: parsedData.skills.map(s => s.name),
        target_role: targetRole.trim() || null
      };

      const response = await axios.post('/api/v1/career-paths', payload);
      setPaths(response.data);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch career paths.');
    } finally {
      setLoading(false);
    }
  };

  // Auto-fetch on mount if we have data, or wait for user input?
  // Let's wait for user to confirm or enter target role.

  return (
    <div className="max-w-4xl mx-auto mt-8 p-6">
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Career Path Discovery</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Current Role</label>
            <div className="p-2 bg-gray-100 rounded border border-gray-300 text-gray-700">
              {parsedData.current_role}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Role (Optional)</label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              placeholder="e.g. Senior Software Engineer"
              className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        <button
          onClick={fetchCareerPaths}
          disabled={loading}
          className="mt-6 bg-green-600 text-white py-2 px-6 rounded hover:bg-green-700 transition-colors disabled:bg-gray-400"
        >
          {loading ? 'Generating Paths...' : 'Find Career Paths'}
        </button>
        {error && <p className="mt-4 text-red-500">{error}</p>}
      </div>

      {paths && (
        <div className="space-y-6">
          <h3 className="text-xl font-semibold text-gray-800">Recommended Paths</h3>
          
          {paths.paths.map((path, index) => (
            <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200 hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                      Score: {Math.round(path.score * 100)}
                    </span>
                    <h4 className="text-lg font-bold text-gray-900">Path {index + 1}</h4>
                  </div>
                  <div className="flex items-center text-gray-500 text-sm">
                    <Clock className="w-4 h-4 mr-1" />
                    {path.timeline_months} months
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2 mb-6">
                  {path.roles.map((role, i) => (
                    <React.Fragment key={i}>
                      <span className="px-3 py-1 bg-gray-100 rounded-full text-sm font-medium text-gray-700">
                        {role}
                      </span>
                      {i < path.roles.length - 1 && <ArrowRight className="w-4 h-4 text-gray-400" />}
                    </React.Fragment>
                  ))}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="flex items-center p-3 bg-green-50 rounded-lg">
                    <TrendingUp className="w-5 h-5 text-green-600 mr-3" />
                    <div>
                      <p className="text-xs text-gray-500">Salary Growth</p>
                      <p className="font-semibold text-green-700">+${path.salary_growth.toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center p-3 bg-purple-50 rounded-lg">
                    <Award className="w-5 h-5 text-purple-600 mr-3" />
                    <div>
                      <p className="text-xs text-gray-500">Skill Match</p>
                      <p className="font-semibold text-purple-700">{path.skill_match.toFixed(1)}%</p>
                    </div>
                  </div>
                  <div className="flex items-center p-3 bg-orange-50 rounded-lg">
                    <AlertCircle className="w-5 h-5 text-orange-600 mr-3" />
                    <div>
                      <p className="text-xs text-gray-500">Difficulty</p>
                      <p className="font-semibold text-orange-700">{path.difficulty.toFixed(1)}/10</p>
                    </div>
                  </div>
                </div>

                {path.missing_skills && path.missing_skills.length > 0 && (
                  <div className="border-t pt-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Skills to Acquire:</p>
                    <div className="flex flex-wrap gap-2">
                      {path.missing_skills.map((skill, i) => (
                        <span key={i} className="px-2 py-1 bg-red-50 text-red-700 text-xs rounded border border-red-100">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CareerPaths;
