import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, Loader2 } from 'lucide-react';

const ResumeUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/v1/resume/parse', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      onUploadSuccess(response.data);
    } catch (err) {
      console.error(err);
      setError('Failed to parse resume. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md max-w-md mx-auto mt-10">
      <h2 className="text-2xl font-bold mb-4 text-center text-gray-800">Upload Your Resume</h2>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={handleFileChange}
          className="hidden"
          id="resume-upload"
        />
        <label htmlFor="resume-upload" className="cursor-pointer flex flex-col items-center">
          <Upload className="w-12 h-12 text-gray-400 mb-2" />
          <span className="text-gray-600">Click to upload PDF or DOCX</span>
        </label>
      </div>

      {file && (
        <div className="mt-4 flex items-center p-3 bg-blue-50 rounded text-blue-700">
          <FileText className="w-5 h-5 mr-2" />
          <span className="truncate">{file.name}</span>
        </div>
      )}

      {error && (
        <div className="mt-4 text-red-500 text-sm text-center">
          {error}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className={`w-full mt-6 py-2 px-4 rounded-md text-white font-medium flex items-center justify-center
          ${!file || loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}
        `}
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
            Parsing...
          </>
        ) : (
          'Analyze Resume'
        )}
      </button>
    </div>
  );
};

export default ResumeUpload;
