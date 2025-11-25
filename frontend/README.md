# Career Navigation Frontend

This is the React frontend for the Career Navigation Platform.

## Prerequisites

- Node.js (v16 or higher)
- npm (v8 or higher)

## Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Start the development server:
    ```bash
    npm run dev
    ```

## Configuration

The frontend is configured to proxy API requests to `http://localhost:8000`. Ensure your backend FastAPI server is running on this port.

## Features

- **Resume Upload**: Upload PDF or DOCX resumes for AI analysis.
- **Dashboard**: View parsed skills and experience.
- **Career Paths**: Explore personalized career trajectories with skill gap analysis.
