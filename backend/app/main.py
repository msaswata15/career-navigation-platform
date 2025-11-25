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
    """Get personalized career paths - supports both same-industry and cross-industry transitions"""
    try:
        print(f"[DEBUG] Received request: current_role='{request.current_role}', target_role='{request.target_role}', user_skills={request.user_skills[:5] if request.user_skills else []}")
        
        # Find paths in graph
        paths = career_graph.find_career_paths(
            current_role=request.current_role,
            target_role=request.target_role
        )
        print(f"[DEBUG] Found {len(paths)} paths from graph")
        
        # If no paths found and target role specified, check for cross-industry transition
        if not paths and request.target_role:
            print(f"[DEBUG] No paths found in database - checking for cross-industry transition")
            cross_industry_guidance = await generate_cross_industry_path(
                current_role=request.current_role,
                target_role=request.target_role,
                user_skills=request.user_skills
            )
            
            if cross_industry_guidance:
                return cross_industry_guidance
        
        # Analyze skill gaps for each path
        analyzed_paths = []
        skill_gap_details = []
        for path in paths:
            skill_gap = skill_db.match_user_skills_to_role(
                user_skills=request.user_skills,
                role_required_skills=path.required_skills
            )

            # Enrich transitions with skill matching for each step
            enriched_transitions = []
            if path.transitions:
                for trans in path.transitions:
                    step_skill_gap = skill_db.match_user_skills_to_role(
                        user_skills=request.user_skills,
                        role_required_skills=trans['required_skills']
                    )
                    enriched_transitions.append({
                        **trans,
                        'skills_to_learn': step_skill_gap['missing_skills'],
                        'skills_match': step_skill_gap['matched_skills']
                    })
            
            analyzed_paths.append({
                'roles': path.roles,
                'timeline_months': path.total_months,
                'difficulty': path.avg_difficulty,
                'salary_growth': path.salary_growth,
                'skill_match': skill_gap['match_percentage'],
                'missing_skills': skill_gap['missing_skills'],
                'matched_skills': skill_gap['matched_skills'],
                'transitions': enriched_transitions
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

async def generate_cross_industry_path(current_role: str, target_role: str, user_skills: List[str]) -> Optional[Dict]:
    """Generate AI-powered guidance for cross-industry career transitions"""
    try:
        import google.generativeai as genai
        import asyncio
        
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        skills_text = ", ".join(user_skills[:10]) if user_skills else "Not specified"
        
        prompt = f"""You are an expert career counselor specializing in cross-industry career transitions.

CURRENT SITUATION:
- Current Role: {current_role}
- Current Skills: {skills_text}
- Target Role: {target_role}

TASK: Create a realistic step-by-step career transition plan from {current_role} to {target_role}.

IMPORTANT: This is a cross-industry transition. Provide practical, actionable guidance including:
1. Feasibility assessment (is this transition realistic?)
2. Estimated timeline (in months)
3. Key steps/milestones with specific actions
4. Skills to acquire for each step
5. Transferable skills from current role
6. Potential challenges and how to overcome them
7. Alternative intermediate roles to consider
8. Estimated difficulty (1-10 scale)

Return your response as a JSON object with this exact structure:
{{
  "is_feasible": true/false,
  "feasibility_note": "explanation of why this transition is or isn't feasible",
  "estimated_timeline_months": number,
  "difficulty_rating": number (1-10),
  "transferable_skills": ["skill1", "skill2", ...],
  "transition_steps": [
    {{
      "step": 1,
      "title": "Step title",
      "description": "Detailed description",
      "duration_months": number,
      "skills_to_acquire": ["skill1", "skill2", ...],
      "actions": ["action1", "action2", ...]
    }}
  ],
  "challenges": ["challenge1", "challenge2", ...],
  "success_tips": ["tip1", "tip2", ...],
  "alternative_paths": ["alternative role 1", "alternative role 2", ...]
}}

Be realistic and honest. If the transition is extremely difficult or unlikely, say so and suggest more feasible alternatives."""

        # Run Gemini API call in thread pool to avoid blocking
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )
        
        response_text = response.text.strip()
        
        # Extract JSON from response (handle markdown code blocks)
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        import json
        guidance = json.loads(response_text)
        
        print(f"[DEBUG] Generated cross-industry guidance: feasible={guidance.get('is_feasible')}")
        
        # Format as career path response
        if guidance.get('is_feasible'):
            # Create synthetic path for UI
            steps = guidance.get('transition_steps', [])
            
            transitions = []
            for i, step in enumerate(steps):
                transitions.append({
                    'step': step.get('step', i + 1),
                    'from_role': current_role if i == 0 else steps[i-1].get('title', f"Step {i}"),
                    'to_role': step.get('title', f"Step {i+1}"),
                    'duration_months': step.get('duration_months', 12),
                    'difficulty': guidance.get('difficulty_rating', 7),
                    'success_rate': max(0.3, 1.0 - (guidance.get('difficulty_rating', 7) / 15)),
                    'salary_from': 0,
                    'salary_to': 0,
                    'salary_increase': 0,
                    'required_skills': step.get('skills_to_acquire', []),
                    'description': step.get('description', ''),
                    'actions': step.get('actions', [])
                })
            
            path = {
                'roles': [current_role] + [s.get('title', f"Step {i+1}") for i, s in enumerate(steps)] + [target_role],
                'timeline_months': guidance.get('estimated_timeline_months', sum(s.get('duration_months', 12) for s in steps)),
                'difficulty': guidance.get('difficulty_rating', 7),
                'salary_growth': 0,  # Unknown for cross-industry
                'skill_match': 0,
                'missing_skills': [skill for step in steps for skill in step.get('skills_to_acquire', [])],
                'matched_skills': guidance.get('transferable_skills', []),
                'transitions': transitions,
                'is_cross_industry': True,
                'feasibility_note': guidance.get('feasibility_note', ''),
                'challenges': guidance.get('challenges', []),
                'success_tips': guidance.get('success_tips', []),
                'alternative_paths': guidance.get('alternative_paths', [])
            }
            
            return {
                'paths': [path],
                'recommended_path': path,
                'skill_gaps': [{
                    'roles': path['roles'],
                    'match_percentage': 0,
                    'matched_skills': guidance.get('transferable_skills', []),
                    'missing_skills': path['missing_skills']
                }]
            }
        else:
            # Not feasible - return guidance with alternatives
            return {
                'paths': [],
                'recommended_path': {
                    'is_cross_industry': True,
                    'is_feasible': False,
                    'feasibility_note': guidance.get('feasibility_note', 'This transition is very challenging'),
                    'alternative_paths': guidance.get('alternative_paths', []),
                    'challenges': guidance.get('challenges', [])
                },
                'skill_gaps': []
            }
            
    except Exception as e:
        print(f"[ERROR] Cross-industry guidance generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

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
