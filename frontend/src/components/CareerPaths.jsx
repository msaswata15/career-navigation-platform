import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  ArrowRight, TrendingUp, Clock, Award, AlertCircle, ChevronDown, ChevronUp, 
  BookOpen, Target, DollarSign, Zap, ExternalLink, Youtube, FileText, 
  GraduationCap, Code, Users, Award as CertIcon, Star, Filter, Search,
  TrendingDown, CheckCircle, Info, BookMarked, Lightbulb, MapPin, Rocket
} from 'lucide-react';

const CareerPaths = ({ parsedData }) => {
  const [paths, setPaths] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [targetRole, setTargetRole] = useState('');
  const [expandedPath, setExpandedPath] = useState(null);
  const [expandedStep, setExpandedStep] = useState({});
  const [selectedFilter, setSelectedFilter] = useState('all'); // all, high-match, fast-track, high-salary
  const [showResourcesType, setShowResourcesType] = useState('all'); // all, free, paid
  const [activeTab, setActiveTab] = useState('overview'); // overview, resources, community

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
      if (response.data.paths && response.data.paths.length > 0) {
        setExpandedPath(0); // Auto-expand first path
      }
    } catch (err) {
      console.error(err);
      setError('Failed to fetch career paths.');
    } finally {
      setLoading(false);
    }
  };

  const toggleStep = (pathIndex, stepIndex) => {
    const key = `${pathIndex}-${stepIndex}`;
    setExpandedStep(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const getFilteredPaths = () => {
    if (!paths || !paths.paths) return [];
    
    let filtered = [...paths.paths];
    
    switch(selectedFilter) {
      case 'high-match':
        return filtered.sort((a, b) => (b.skill_match || 0) - (a.skill_match || 0));
      case 'fast-track':
        return filtered.sort((a, b) => (a.timeline_months || 999) - (b.timeline_months || 999));
      case 'high-salary':
        return filtered.sort((a, b) => (b.salary_growth || 0) - (a.salary_growth || 0));
      default:
        return filtered.sort((a, b) => (b.score || 0) - (a.score || 0));
    }
  };

  const getScoreColor = (score) => {
    if (score >= 70) return 'bg-green-500 text-white';
    if (score >= 50) return 'bg-yellow-500 text-white';
    return 'bg-orange-500 text-white';
  };

  const getDifficultyColor = (difficulty) => {
    if (difficulty <= 3) return 'text-green-600 bg-green-50';
    if (difficulty <= 6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getDifficultyLabel = (difficulty) => {
    if (difficulty <= 3) return 'Easy';
    if (difficulty <= 6) return 'Moderate';
    return 'Challenging';
  };

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
            <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200 hover:shadow-xl transition-all">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                      Score: {Math.round(path.score * 100)}
                    </span>
                    {index === 0 && (
                      <span className="bg-green-100 text-green-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                        ⭐ Recommended
                      </span>
                    )}
                    <h4 className="text-lg font-bold text-gray-900">Path {index + 1}</h4>
                  </div>
                  <div className="flex items-center text-gray-500 text-sm">
                    <Clock className="w-4 h-4 mr-1" />
                    {path.timeline_months} months total
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2 mb-6">
                  {path.roles.map((role, i) => (
                    <React.Fragment key={i}>
                      <span className="px-3 py-1 bg-gradient-to-r from-blue-100 to-blue-50 rounded-full text-sm font-medium text-gray-700 border border-blue-200">
                        {role}
                      </span>
                      {i < path.roles.length - 1 && <ArrowRight className="w-4 h-4 text-blue-500" />}
                    </React.Fragment>
                  ))}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="flex items-center p-3 bg-green-50 rounded-lg border border-green-200">
                    <TrendingUp className="w-5 h-5 text-green-600 mr-3" />
                    <div>
                      <p className="text-xs text-gray-500">Salary Growth</p>
                      <p className="font-semibold text-green-700">+${path.salary_growth.toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center p-3 bg-purple-50 rounded-lg border border-purple-200">
                    <Award className="w-5 h-5 text-purple-600 mr-3" />
                    <div>
                      <p className="text-xs text-gray-500">Skill Match</p>
                      <p className="font-semibold text-purple-700">{path.skill_match.toFixed(1)}%</p>
                    </div>
                  </div>
                  <div className="flex items-center p-3 bg-orange-50 rounded-lg border border-orange-200">
                    <AlertCircle className="w-5 h-5 text-orange-600 mr-3" />
                    <div>
                      <p className="text-xs text-gray-500">Difficulty</p>
                      <p className="font-semibold text-orange-700">{path.difficulty.toFixed(1)}/10</p>
                    </div>
                  </div>
                  <div className="flex items-center p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <Target className="w-5 h-5 text-blue-600 mr-3" />
                    <div>
                      <p className="text-xs text-gray-500">Steps</p>
                      <p className="font-semibold text-blue-700">{path.transitions?.length || 0}</p>
                    </div>
                  </div>
                </div>

                {/* Matched Skills */}
                {path.matched_skills && path.matched_skills.length > 0 && (
                  <div className="mb-4 pb-4 border-b">
                    <p className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                      <Award className="w-4 h-4 mr-1 text-green-600" />
                      Your Matching Skills ({path.matched_skills.length}):
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {path.matched_skills.map((skill, i) => (
                        <span key={i} className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded border border-green-200 font-medium">
                          ✓ {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Overall Missing Skills */}
                {path.missing_skills && path.missing_skills.length > 0 && (
                  <div className="mb-4 pb-4 border-b">
                    <p className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                      <BookOpen className="w-4 h-4 mr-1 text-red-600" />
                      Skills to Acquire for Final Role:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {path.missing_skills.map((skill, i) => (
                        <span key={i} className="px-2 py-1 bg-red-50 text-red-700 text-xs rounded border border-red-200 font-medium">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Step-by-Step Breakdown */}
                {path.transitions && path.transitions.length > 0 && (
                  <div>
                    <button
                      onClick={() => setExpandedPath(expandedPath === index ? null : index)}
                      className="w-full flex items-center justify-between p-3 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg hover:from-indigo-100 hover:to-purple-100 transition-colors mb-2"
                    >
                      <span className="font-semibold text-indigo-900 flex items-center">
                        <Zap className="w-4 h-4 mr-2" />
                        Step-by-Step Roadmap ({path.transitions.length} steps)
                      </span>
                      {expandedPath === index ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                    </button>

                    {expandedPath === index && (
                      <div className="space-y-4 mt-4">
                        {path.transitions.map((transition, tIdx) => (
                          <div key={tIdx} className="ml-4 pl-4 border-l-4 border-indigo-300 py-3">
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex-1">
                                <div className="flex items-center mb-2">
                                  <span className="bg-indigo-600 text-white text-xs font-bold px-2 py-1 rounded-full mr-2">
                                    Step {transition.step}
                                  </span>
                                  <span className="text-sm text-gray-600">
                                    {transition.from_role} → {transition.to_role}
                                  </span>
                                </div>
                                
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                                  <div className="bg-blue-50 p-2 rounded border border-blue-200">
                                    <p className="text-xs text-gray-500">Duration</p>
                                    <p className="font-semibold text-blue-700">{transition.duration_months} months</p>
                                  </div>
                                  <div className="bg-green-50 p-2 rounded border border-green-200">
                                    <p className="text-xs text-gray-500">Salary Jump</p>
                                    <p className="font-semibold text-green-700">+${transition.salary_increase.toLocaleString()}</p>
                                  </div>
                                  <div className="bg-purple-50 p-2 rounded border border-purple-200">
                                    <p className="text-xs text-gray-500">Success Rate</p>
                                    <p className="font-semibold text-purple-700">{(transition.success_rate * 100).toFixed(0)}%</p>
                                  </div>
                                  <div className="bg-orange-50 p-2 rounded border border-orange-200">
                                    <p className="text-xs text-gray-500">Difficulty</p>
                                    <p className="font-semibold text-orange-700">{transition.difficulty}/10</p>
                                  </div>
                                </div>

                                {transition.skills_to_learn && transition.skills_to_learn.length > 0 && (
                                  <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                                    <p className="text-xs font-semibold text-yellow-800 mb-2 flex items-center">
                                      <BookOpen className="w-3 h-3 mr-1" />
                                      Skills to Learn for This Step:
                                    </p>
                                    <div className="flex flex-wrap gap-1">
                                      {transition.skills_to_learn.map((skill, sIdx) => (
                                        <span key={sIdx} className="px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs rounded border border-yellow-300">
                                          📚 {skill}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Learning Resources Section */}
                                {transition.learning_resources && transition.learning_resources.length > 0 && (
                                  <div className="mt-3 bg-indigo-50 p-4 rounded-lg border border-indigo-200">
                                    <p className="text-sm font-bold text-indigo-900 mb-3 flex items-center">
                                      <GraduationCap className="w-4 h-4 mr-2" />
                                      📖 Learning Resources ({transition.learning_resources.length})
                                    </p>
                                    <div className="space-y-3">
                                      {transition.learning_resources.map((resource, rIdx) => (
                                        <div key={rIdx} className="bg-white p-3 rounded-lg border border-indigo-300 hover:shadow-md transition-shadow">
                                          <div className="flex items-start justify-between mb-2">
                                            <div className="flex-1">
                                              <div className="flex items-center mb-1">
                                                {resource.resource_type === 'youtube' && <Youtube className="w-4 h-4 mr-2 text-red-600" />}
                                                {resource.resource_type === 'course' && <GraduationCap className="w-4 h-4 mr-2 text-blue-600" />}
                                                {resource.resource_type === 'documentation' && <FileText className="w-4 h-4 mr-2 text-gray-600" />}
                                                {resource.resource_type === 'certification' && <CertIcon className="w-4 h-4 mr-2 text-purple-600" />}
                                                {resource.resource_type === 'book' && <BookOpen className="w-4 h-4 mr-2 text-amber-600" />}
                                                <a 
                                                  href={resource.url.startsWith('http') ? resource.url : `https://www.google.com/search?q=${encodeURIComponent(resource.url)}`}
                                                  target="_blank"
                                                  rel="noopener noreferrer"
                                                  className="font-semibold text-indigo-700 hover:text-indigo-900 hover:underline text-sm"
                                                >
                                                  {resource.title}
                                                </a>
                                                <ExternalLink className="w-3 h-3 ml-1 text-gray-400" />
                                              </div>
                                              <p className="text-xs text-gray-600 mb-2">
                                                <span className="font-medium">Skill:</span> {resource.skill} • 
                                                <span className="ml-1 font-medium">Provider:</span> {resource.provider}
                                              </p>
                                              <div className="flex flex-wrap gap-2 mb-2">
                                                <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">
                                                  ⏱️ {resource.duration}
                                                </span>
                                                <span className={`px-2 py-0.5 text-xs rounded ${
                                                  resource.cost === 'Free' ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
                                                }`}>
                                                  💰 {resource.cost}
                                                </span>
                                                <span className={`px-2 py-0.5 text-xs rounded ${
                                                  resource.difficulty === 'Beginner' ? 'bg-green-100 text-green-700' :
                                                  resource.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-700' :
                                                  'bg-red-100 text-red-700'
                                                }`}>
                                                  📊 {resource.difficulty}
                                                </span>
                                              </div>
                                              <p className="text-xs text-gray-600 italic">
                                                ✨ {resource.why_recommended}
                                              </p>
                                            </div>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Certifications Section */}
                                {transition.certifications && transition.certifications.length > 0 && (
                                  <div className="mt-3 bg-purple-50 p-4 rounded-lg border border-purple-200">
                                    <p className="text-sm font-bold text-purple-900 mb-3 flex items-center">
                                      <CertIcon className="w-4 h-4 mr-2" />
                                      🎓 Certifications ({transition.certifications.length})
                                    </p>
                                    <div className="space-y-3">
                                      {transition.certifications.map((cert, cIdx) => (
                                        <div key={cIdx} className="bg-white p-3 rounded-lg border border-purple-300">
                                          <div className="flex items-start justify-between mb-2">
                                            <div className="flex-1">
                                              <div className="flex items-center mb-1">
                                                <a 
                                                  href={cert.url.startsWith('http') ? cert.url : `https://www.google.com/search?q=${encodeURIComponent(cert.url)}`}
                                                  target="_blank"
                                                  rel="noopener noreferrer"
                                                  className="font-semibold text-purple-700 hover:text-purple-900 hover:underline text-sm"
                                                >
                                                  {cert.name}
                                                </a>
                                                <ExternalLink className="w-3 h-3 ml-1 text-gray-400" />
                                                <span className={`ml-2 px-2 py-0.5 text-xs rounded ${
                                                  cert.importance === 'Required' ? 'bg-red-100 text-red-700 font-bold' :
                                                  cert.importance === 'Highly Recommended' ? 'bg-orange-100 text-orange-700' :
                                                  'bg-gray-100 text-gray-700'
                                                }`}>
                                                  {cert.importance}
                                                </span>
                                              </div>
                                              <p className="text-xs text-gray-600 mb-1">
                                                <span className="font-medium">Provider:</span> {cert.provider}
                                              </p>
                                              <div className="flex flex-wrap gap-2">
                                                <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">
                                                  📅 Study: {cert.study_duration}
                                                </span>
                                                <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded">
                                                  💵 ${cert.estimated_cost}
                                                </span>
                                                <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs rounded">
                                                  ⏰ Valid: {cert.validity}
                                                </span>
                                              </div>
                                            </div>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Practical Projects Section */}
                                {transition.practical_projects && transition.practical_projects.length > 0 && (
                                  <div className="mt-3 bg-teal-50 p-4 rounded-lg border border-teal-200">
                                    <p className="text-sm font-bold text-teal-900 mb-3 flex items-center">
                                      <Code className="w-4 h-4 mr-2" />
                                      🛠️ Practical Projects ({transition.practical_projects.length})
                                    </p>
                                    <div className="space-y-2">
                                      {transition.practical_projects.map((project, pIdx) => (
                                        <div key={pIdx} className="bg-white p-3 rounded-lg border border-teal-300">
                                          <p className="font-semibold text-teal-700 text-sm mb-1">{project.project_title}</p>
                                          <p className="text-xs text-gray-600 mb-2">{project.description}</p>
                                          <div className="flex items-center gap-2">
                                            <span className="px-2 py-0.5 bg-teal-100 text-teal-700 text-xs rounded">
                                              ⏱️ {project.estimated_time}
                                            </span>
                                            {project.resources && project.resources.length > 0 && (
                                              <span className="text-xs text-gray-500">
                                                📚 {project.resources.join(', ')}
                                              </span>
                                            )}
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {transition.skills_match && transition.skills_match.length > 0 && (
                                  <div className="bg-green-50 p-3 rounded-lg border border-green-200 mt-2">
                                    <p className="text-xs font-semibold text-green-800 mb-2">
                                      ✓ Skills You Already Have:
                                    </p>
                                    <div className="flex flex-wrap gap-1">
                                      {transition.skills_match.map((skill, sIdx) => (
                                        <span key={sIdx} className="px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded">
                                          {skill}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                        
                        <div className="ml-4 mt-4 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border-2 border-green-300">
                          <p className="font-bold text-green-800 flex items-center mb-2">
                            <Target className="w-5 h-5 mr-2" />
                            Final Destination
                          </p>
                          <p className="text-lg font-semibold text-gray-900 mb-2">{path.roles[path.roles.length - 1]}</p>
                          <div className="flex items-center text-green-700">
                            <DollarSign className="w-4 h-4 mr-1" />
                            <span className="font-semibold">Total Salary Increase: +${path.salary_growth.toLocaleString()}</span>
                          </div>
                        </div>

                        {/* Community Resources */}
                        {path.community_resources && path.community_resources.length > 0 && (
                          <div className="ml-4 mt-4 bg-blue-50 p-4 rounded-lg border border-blue-200">
                            <p className="text-sm font-bold text-blue-900 mb-3 flex items-center">
                              <Users className="w-4 h-4 mr-2" />
                              👥 Community & Support
                            </p>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                              {path.community_resources.map((community, cIdx) => (
                                <div key={cIdx} className="bg-white p-3 rounded-lg border border-blue-300">
                                  <div className="flex items-center mb-1">
                                    <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded mr-2 font-semibold">
                                      {community.type}
                                    </span>
                                    <a 
                                      href={community.url.startsWith('http') ? community.url : `https://www.google.com/search?q=${encodeURIComponent(community.url)}`}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="font-semibold text-blue-700 hover:text-blue-900 hover:underline text-sm"
                                    >
                                      {community.name}
                                    </a>
                                    <ExternalLink className="w-3 h-3 ml-1 text-gray-400" />
                                  </div>
                                  <p className="text-xs text-gray-600">{community.description}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Mentorship Opportunities */}
                        {path.mentorship_opportunities && path.mentorship_opportunities.length > 0 && (
                          <div className="ml-4 mt-4 bg-amber-50 p-4 rounded-lg border border-amber-200">
                            <p className="text-sm font-bold text-amber-900 mb-3 flex items-center">
                              <Users className="w-4 h-4 mr-2" />
                              🤝 Find a Mentor
                            </p>
                            <ul className="space-y-2">
                              {path.mentorship_opportunities.map((opportunity, mIdx) => (
                                <li key={mIdx} className="flex items-start">
                                  <span className="text-amber-600 mr-2">•</span>
                                  <span className="text-sm text-gray-700">{opportunity}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
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
