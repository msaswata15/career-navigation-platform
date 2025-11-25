"""
Vector database for semantic skill matching using Pinecone
"""

import pinecone
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np

class SkillVectorDB:
    def __init__(self, pinecone_api_key: str, index_name: str = "career-skills"):
        # Initialize Pinecone
        pinecone.init(api_key=pinecone_api_key, environment="us-west1-gcp")
        
        # Create or connect to index
        try:
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    index_name,
                    dimension=384,  # all-MiniLM-L6-v2 embedding size
                    metric="cosine"
                )
        except Exception as e:
            print(f"Warning: Index creation/check failed: {e}")
            print("Attempting to connect to index anyway...")
        
        self.index = pinecone.Index(index_name)
        
        # Load sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_skills(self, skills: List[Dict]):
        """Add skills to vector database
        
        Args:
            skills: List of dicts with 'id', 'name', 'category', 'demand_score'
        """
        vectors = []
        for skill in skills:
            # Generate embedding
            embedding = self.model.encode(skill['name']).tolist()
            
            vectors.append({
                'id': skill['id'],
                'values': embedding,
                'metadata': {
                    'name': skill['name'],
                    'category': skill.get('category', 'general'),
                    'demand_score': skill.get('demand_score', 50)
                }
            })
        
        # Upsert to Pinecone
        self.index.upsert(vectors=vectors)
    
    def find_similar_skills(self, skill_name: str, top_k: int = 5) -> List[Dict]:
        """Find semantically similar skills"""
        
        # Generate query embedding
        query_embedding = self.model.encode(skill_name).tolist()
        
        # Search in Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        similar_skills = []
        for match in results['matches']:
            similar_skills.append({
                'skill': match['metadata']['name'],
                'category': match['metadata']['category'],
                'similarity_score': match['score'],
                'demand_score': match['metadata']['demand_score']
            })
        
        return similar_skills
    
    def match_user_skills_to_role(self, user_skills: List[str], 
                                   role_required_skills: List[str]) -> Dict:
        """Match user skills against role requirements"""
        
        if not role_required_skills:
            return {
                'match_percentage': 0.0,
                'matched_skills': [],
                'missing_skills': []
            }

        if not user_skills:
            return {
                'match_percentage': 0.0,
                'matched_skills': [],
                'missing_skills': role_required_skills
            }

        matched_skills = []
        missing_skills = []
        
        for required_skill in role_required_skills:
            # Find if user has similar skill
            user_embeddings = self.model.encode(user_skills)
            required_embedding = self.model.encode(required_skill)
            
            # Calculate cosine similarities
            similarities = np.dot(user_embeddings, required_embedding) / (
                np.linalg.norm(user_embeddings, axis=1) * np.linalg.norm(required_embedding)
            )
            
            max_similarity = similarities.max()
            
            if max_similarity > 0.7:  # Threshold for "match"
                matched_idx = similarities.argmax()
                matched_skills.append({
                    'required': required_skill,
                    'user_has': user_skills[matched_idx],
                    'match_score': float(max_similarity)
                })
            else:
                missing_skills.append(required_skill)
        
        match_percentage = (len(matched_skills) / len(role_required_skills)) * 100 if role_required_skills else 0.0
        
        return {
            'match_percentage': match_percentage,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills
        }

if __name__ == "__main__":
    # Usage
    vector_db = SkillVectorDB(pinecone_api_key="your-key")

    # Add skills to database
    skills = [
        {'id': 'python-001', 'name': 'Python', 'category': 'programming', 'demand_score': 95},
        {'id': 'django-001', 'name': 'Django', 'category': 'framework', 'demand_score': 75},
        # ... more skills
    ]
    vector_db.add_skills(skills)

    # Find similar skills
    similar = vector_db.find_similar_skills("Machine Learning")
