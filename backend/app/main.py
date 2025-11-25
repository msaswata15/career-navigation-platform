"""
Main FastAPI application
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
import os

from app.core.ai_parser import AIResumeParser
from app.models.user import ParsedResume
from app.models.career import CareerPathRequest, CareerPathResponse
from app.utils.pdf_parser import extract_text
from app.services.vector_db import SkillVectorDB
from app.services.graph_db import CareerGraphDB, CareerPath
from app.services.cache import RedisCache

# Initialize FastAPI
app = FastAPI(
    title="Career Navigation API",
    description="AI-powered career path discovery platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.config import settings

# Initialize services
resume_parser = AIResumeParser(google_api_key=settings.GOOGLE_API_KEY)
skill_db = SkillVectorDB(pinecone_api_key=settings.PINECONE_API_KEY)
career_graph = CareerGraphDB(
    uri=settings.NEO4J_URI,
    user=settings.NEO4J_USER,
    password=settings.NEO4J_PASSWORD,
    google_api_key=settings.GOOGLE_API_KEY
)
cache = RedisCache(redis_url=settings.REDIS_URL)

# API Endpoints

@app.post("/api/v1/resume/parse", response_model=ParsedResume)
async def parse_resume(file: UploadFile = File(...)):
    """Parse uploaded resume"""
    try:
        # Read file
        contents = await file.read()
        
        # Check cache
        cache_key = f"resume:{file.filename}"
        cached = await cache.get(cache_key)
        if cached:
            return cached
        
        # Parse resume
        text = extract_text(contents, file.filename)
        parsed_data = await resume_parser.parse_resume(text)
        
        # Cache result
        await cache.set(cache_key, parsed_data.dict(), expire=3600)
        
        return parsed_data
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/career-paths", response_model=CareerPathResponse)
async def get_career_paths(request: CareerPathRequest):
    """Get personalized career paths"""
    try:
        print(f"[DEBUG] Received request: current_role='{request.current_role}', target_role='{request.target_role}', user_skills={request.user_skills[:5] if request.user_skills else []}")
        
        # Find paths in graph
        paths = career_graph.find_career_paths(
            current_role=request.current_role,
            target_role=request.target_role
        )
        print(f"[DEBUG] Found {len(paths)} paths from graph")
        
        # Analyze skill gaps for each path
        analyzed_paths = []
        skill_gap_details = []
        for path in paths:
            skill_gap = skill_db.match_user_skills_to_role(
                user_skills=request.user_skills,
                role_required_skills=path.required_skills
            )

            analyzed_paths.append({
                'roles': path.roles,
                'timeline_months': path.total_months,
                'difficulty': path.avg_difficulty,
                'salary_growth': path.salary_growth,
                'skill_match': skill_gap['match_percentage'],
                'missing_skills': skill_gap['missing_skills']
            })

            skill_gap_details.append({
                'roles': path.roles,
                'match_percentage': skill_gap['match_percentage'],
                'matched_skills': skill_gap['matched_skills'],
                'missing_skills': skill_gap['missing_skills']
            })

        if not analyzed_paths:
            return {
                'paths': [],
                'recommended_path': None,
                'skill_gaps': skill_gap_details
            }

        # Rank paths by overall score
        for path in analyzed_paths:
            path['score'] = calculate_path_score(path)

        analyzed_paths.sort(key=lambda x: x['score'], reverse=True)

        return {
            'paths': analyzed_paths,
            'recommended_path': analyzed_paths[0],
            'skill_gaps': skill_gap_details
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

def calculate_path_score(path: Dict) -> float:
    """Calculate overall path score"""
    weights = {
        'skill_match': 0.4,
        'salary_growth': 0.3,
        'timeline': 0.2,
        'difficulty': 0.1
    }
    
    # Normalize values
    skill_score = path['skill_match'] / 100
    salary_score = min(path['salary_growth'] / 50000, 1.0)
    timeline_score = 1 - (path['timeline_months'] / 60)
    difficulty_score = 1 - (path['difficulty'] / 10)
    
    return (
        weights['skill_match'] * skill_score +
        weights['salary_growth'] * salary_score +
        weights['timeline'] * timeline_score +
        weights['difficulty'] * difficulty_score
    )

@app.get("/api/v1/skills/similar/{skill_name}")
async def find_similar_skills(skill_name: str, limit: int = 5):
    """Find semantically similar skills"""
    similar = skill_db.find_similar_skills(skill_name, top_k=limit)
    return {'similar_skills': similar}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
