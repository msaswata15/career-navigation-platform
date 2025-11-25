import os
import sys
from dotenv import load_dotenv

# Add backend directory to path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.vector_db import SkillVectorDB

load_dotenv()

def update_embeddings():
    print("Updating skill embeddings...")
    
    vector_db = SkillVectorDB(
        pinecone_api_key=os.getenv("PINECONE_API_KEY", "your-key")
    )
    
    # Define skills to add
    skills = [
        {'id': 'python', 'name': 'Python', 'category': 'programming', 'demand_score': 95},
        {'id': 'java', 'name': 'Java', 'category': 'programming', 'demand_score': 90},
        {'id': 'javascript', 'name': 'JavaScript', 'category': 'programming', 'demand_score': 92},
        {'id': 'react', 'name': 'React', 'category': 'framework', 'demand_score': 88},
        {'id': 'fastapi', 'name': 'FastAPI', 'category': 'framework', 'demand_score': 85},
        {'id': 'machine-learning', 'name': 'Machine Learning', 'category': 'domain', 'demand_score': 94},
        {'id': 'data-analysis', 'name': 'Data Analysis', 'category': 'domain', 'demand_score': 89},
        {'id': 'system-design', 'name': 'System Design', 'category': 'technical', 'demand_score': 87},
        {'id': 'communication', 'name': 'Communication', 'category': 'soft', 'demand_score': 90},
        {'id': 'leadership', 'name': 'Leadership', 'category': 'soft', 'demand_score': 85}
    ]
    
    print(f"Adding {len(skills)} skills to vector database...")
    vector_db.add_skills(skills)
    print("Embeddings updated.")

if __name__ == "__main__":
    update_embeddings()
