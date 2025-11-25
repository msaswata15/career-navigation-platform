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
        

        import google.generativeai as genai
        import asyncio
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")

        async def enrich_step_with_gemini(step, from_role, to_role, user_skills):
            skills_text = ", ".join(user_skills[:10]) if user_skills else "Not specified"
            prompt = f"""You are an expert career coach. For the transition from '{from_role}' to '{to_role}', provide:
1. 3-5 specific learning resources (YouTube, courses, docs, books, bootcamps) for the most important skills in this step.
2. 1-2 relevant certifications (with provider, cost, and URL or search term).
3. 1-2 practical project ideas (with description and resource links).
4. For each resource, include: skill, resource_type, title, url or search term, provider, duration, cost, difficulty, why_recommended.
5. For each certification: name, provider, estimated_cost, study_duration, validity, url or search term, importance.
6. For each project: project_title, description, estimated_time, resources (links).
Context: User skills: {skills_text}. Step required skills: {', '.join(step.get('required_skills', []))}.
Return as JSON with keys: learning_resources, certifications, practical_projects."""
            response = await asyncio.to_thread(model.generate_content, prompt)
            response_text = response.text.strip()
            import json
            # Extract JSON from response (handle markdown code blocks)
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            try:
                data = json.loads(response_text)
            except Exception:
                data = {}
            return {
                'learning_resources': data.get('learning_resources', []),
                'certifications': data.get('certifications', []),
                'practical_projects': data.get('practical_projects', [])
            }

        analyzed_paths = []
        skill_gap_details = []
        for path in paths:
            skill_gap = skill_db.match_user_skills_to_role(
                user_skills=request.user_skills,
                role_required_skills=path.required_skills
            )

            enriched_transitions = []
            if path.transitions:
                # Enrich each step with Gemini-powered resources
                tasks = []
                for trans in path.transitions:
                    step_skill_gap = skill_db.match_user_skills_to_role(
                        user_skills=request.user_skills,
                        role_required_skills=trans['required_skills']
                    )
                    tasks.append(enrich_step_with_gemini(trans, trans['from_role'], trans['to_role'], request.user_skills))
                gemini_results = await asyncio.gather(*tasks)
                for i, trans in enumerate(path.transitions):
                    step_skill_gap = skill_db.match_user_skills_to_role(
                        user_skills=request.user_skills,
                        role_required_skills=trans['required_skills']
                    )
                    gemini_data = gemini_results[i] if i < len(gemini_results) else {}
                    enriched_transitions.append({
                        **trans,
                        'skills_to_learn': step_skill_gap['missing_skills'],
                        'skills_match': step_skill_gap['matched_skills'],
                        'learning_resources': gemini_data.get('learning_resources', []),
                        'certifications': gemini_data.get('certifications', []),
                        'practical_projects': gemini_data.get('practical_projects', [])
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

IMPORTANT: Provide detailed information including realistic salary data, skill matching, AND comprehensive learning resources.

Return your response as a JSON object with this exact structure:
{{
  "is_feasible": true/false,
  "feasibility_note": "explanation of why this transition is or isn't feasible",
  "estimated_timeline_months": number,
  "difficulty_rating": number (1-10),
  
  "salary_info": {{
    "current_role_avg_salary": number (annual USD),
    "target_role_avg_salary": number (annual USD),
    "initial_salary_drop": number (if any, negative for decrease),
    "long_term_salary_potential": number (after 5 years in new field),
    "salary_note": "explanation of salary trajectory"
  }},
  
  "skill_analysis": {{
    "transferable_skills": ["skill1", "skill2", ...],
    "skill_match_percentage": number (0-100),
    "skills_that_translate": [
      {{"from": "current skill", "to": "how it applies in new role"}}
    ],
    "missing_critical_skills": ["skill1", "skill2", ...]
  }},
  
  "transition_steps": [
    {{
      "step": 1,
      "title": "Step title",
      "description": "Detailed description",
      "duration_months": number,
      "estimated_salary": number (expected earnings during this step),
      "skills_to_acquire": ["skill1", "skill2", ...],
      "actions": ["action1", "action2", ...],
      "estimated_cost": number (tuition, certifications, etc. in USD),
      
      "learning_resources": [
        {{
          "skill": "specific skill name",
          "resource_type": "youtube|course|documentation|certification|book|bootcamp",
          "title": "Resource title",
          "url": "https://actual-url.com OR search term if URL unknown",
          "provider": "YouTube|Coursera|Udemy|edX|Official Docs|etc",
          "duration": "2 hours|4 weeks|3 months|etc",
          "cost": "Free|$49|$299|etc",
          "difficulty": "Beginner|Intermediate|Advanced",
          "why_recommended": "Brief explanation"
        }}
      ],
      
      "certifications": [
        {{
          "name": "Certification name",
          "provider": "Issuing organization",
          "estimated_cost": number,
          "study_duration": "time needed to prepare",
          "validity": "lifetime|2 years|etc",
          "url": "https://certification-url.com OR search term",
          "importance": "Required|Highly Recommended|Optional"
        }}
      ],
      
      "practical_projects": [
        {{
          "project_title": "What to build/do",
          "description": "How it helps learning",
          "estimated_time": "duration",
          "resources": ["link1", "link2"]
        }}
      ]
    }}
  ],
  
  "challenges": ["challenge1", "challenge2", ...],
  "success_tips": ["tip1", "tip2", ...],
  "alternative_paths": ["alternative role 1", "alternative role 2", ...],
  "realistic_success_rate": number (0-100, percentage likelihood of successful transition),
  
  "community_resources": [
    {{
      "type": "Forum|Discord|Reddit|LinkedIn Group|Slack",
      "name": "Community name",
      "url": "URL or search term",
      "description": "What you can get from this community"
    }}
  ],
  
  "mentorship_opportunities": [
    "Where to find mentors in the target field"
  ]
}}

CRITICAL REQUIREMENTS FOR LEARNING RESOURCES:
1. Provide REAL, SPECIFIC resources (actual YouTube channels, course names, documentation sites)
2. For popular transitions, include well-known resources (e.g., for programming: "freeCodeCamp", "The Odin Project")
3. For aviation: FAA handbooks, specific YouTube channels like "Flight Insight", "MzeroA"
4. For data science: "StatQuest", "3Blue1Brown", "Andrew Ng's Machine Learning Course"
5. Include both FREE and PAID options
6. Provide realistic time estimates for each resource
7. Include official documentation URLs where applicable
8. For certifications, mention actual certification names (AWS Certified, Google Cloud, FAA licenses)

EXAMPLES OF GOOD RESOURCES:
- YouTube: "Traversy Media - Full Stack Web Development", "freeCodeCamp Python Tutorial"
- Courses: "CS50 Introduction to Computer Science (Harvard/edX)", "Google Data Analytics Certificate"
- Docs: "MDN Web Docs", "Python Official Tutorial", "React Documentation"
- Certifications: "AWS Solutions Architect", "CompTIA A+", "PMP Certification"

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
        
        print(f"[DEBUG] Generated cross-industry guidance: feasible={guidance.get('is_feasible')}, skill_match={guidance.get('skill_analysis', {}).get('skill_match_percentage', 0)}%")
        
        # Format as career path response
        if guidance.get('is_feasible'):
            # Create synthetic path for UI
            steps = guidance.get('transition_steps', [])
            salary_info = guidance.get('salary_info', {})
            skill_analysis = guidance.get('skill_analysis', {})
            
            current_salary = salary_info.get('current_role_avg_salary', 0)
            target_salary = salary_info.get('target_role_avg_salary', 0)
            
            transitions = []
            for i, step in enumerate(steps):
                step_salary = step.get('estimated_salary', current_salary)
                prev_salary = current_salary if i == 0 else steps[i-1].get('estimated_salary', current_salary)
                
                transitions.append({
                    'step': step.get('step', i + 1),
                    'from_role': current_role if i == 0 else steps[i-1].get('title', f"Step {i}"),
                    'to_role': step.get('title', f"Step {i+1}"),
                    'duration_months': step.get('duration_months', 12),
                    'difficulty': guidance.get('difficulty_rating', 7),
                    'success_rate': guidance.get('realistic_success_rate', 50) / 100,
                    'salary_from': int(prev_salary),
                    'salary_to': int(step_salary),
                    'salary_increase': int(step_salary - prev_salary),
                    'required_skills': step.get('skills_to_acquire', []),
                    'description': step.get('description', ''),
                    'actions': step.get('actions', []),
                    'estimated_cost': step.get('estimated_cost', 0),
                    'learning_resources': step.get('learning_resources', []),
                    'certifications': step.get('certifications', []),
                    'practical_projects': step.get('practical_projects', [])
                })
            
            # Calculate overall salary growth (from current to target)
            final_salary = target_salary or (steps[-1].get('estimated_salary', current_salary) if steps else current_salary)
            salary_growth = int(final_salary - current_salary)
            
            # Get skill match percentage
            skill_match = skill_analysis.get('skill_match_percentage', 0)
            transferable_skills = skill_analysis.get('transferable_skills', [])
            missing_skills = skill_analysis.get('missing_critical_skills', [])
            
            # Add all step-specific skills to missing skills
            all_missing = list(set(missing_skills + [s for step in steps for s in step.get('skills_to_acquire', [])]))
            
            path = {
                'roles': [current_role] + [s.get('title', f"Step {i+1}") for i, s in enumerate(steps)] + [target_role],
                'timeline_months': guidance.get('estimated_timeline_months', sum(s.get('duration_months', 12) for s in steps)),
                'difficulty': guidance.get('difficulty_rating', 7),
                'salary_growth': salary_growth,
                'skill_match': skill_match,
                'missing_skills': all_missing,
                'matched_skills': transferable_skills,
                'transitions': transitions,
                'is_cross_industry': True,
                'feasibility_note': guidance.get('feasibility_note', ''),
                'challenges': guidance.get('challenges', []),
                'success_tips': guidance.get('success_tips', []),
                'alternative_paths': guidance.get('alternative_paths', []),
                'salary_info': {
                    'current_avg': int(current_salary),
                    'target_avg': int(final_salary),
                    'initial_drop': int(salary_info.get('initial_salary_drop', 0)),
                    'long_term_potential': int(salary_info.get('long_term_salary_potential', final_salary)),
                    'note': salary_info.get('salary_note', '')
                },
                'skill_translation': skill_analysis.get('skills_that_translate', []),
                'realistic_success_rate': guidance.get('realistic_success_rate', 50),
                'community_resources': guidance.get('community_resources', []),
                'mentorship_opportunities': guidance.get('mentorship_opportunities', [])
            }
            
            # Calculate path score
            path['score'] = calculate_cross_industry_score(path)
            
            return {
                'paths': [path],
                'recommended_path': path,
                'skill_gaps': [{
                    'roles': path['roles'],
                    'match_percentage': skill_match,
                    'matched_skills': transferable_skills,
                    'missing_skills': all_missing
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

def calculate_cross_industry_score(path: Dict) -> float:
    """Calculate score for cross-industry transitions"""
    # Different weighting for cross-industry transitions
    weights = {
        'skill_match': 0.3,
        'success_rate': 0.25,
        'salary_potential': 0.25,
        'timeline': 0.1,
        'difficulty': 0.1
    }
    
    # Normalize values
    skill_score = path.get('skill_match', 0) / 100
    success_score = path.get('realistic_success_rate', 50) / 100
    
    # Salary potential (considering long-term, not just immediate)
    salary_info = path.get('salary_info', {})
    long_term_potential = salary_info.get('long_term_potential', salary_info.get('target_avg', 0))
    current_salary = salary_info.get('current_avg', 1)
    salary_score = min(max(long_term_potential / max(current_salary, 1), 0), 2) / 2  # Normalize to 0-1
    
    timeline_score = max(0, 1 - (path.get('timeline_months', 24) / 72))  # 6 years max
    difficulty_score = max(0, 1 - (path.get('difficulty', 5) / 10))
    
    score = (
        weights['skill_match'] * skill_score +
        weights['success_rate'] * success_score +
        weights['salary_potential'] * salary_score +
        weights['timeline'] * timeline_score +
        weights['difficulty'] * difficulty_score
    )
    
    return round(score * 100, 2)  # Return as percentage

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
