import os
import sys
from dotenv import load_dotenv

# Add backend directory to path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.graph_db import CareerGraphDB

load_dotenv()

def seed_careers():
    print("Seeding career graph...")
    
    graph_db = CareerGraphDB(
        uri=os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "12345678")
    )
    
    try:
        graph_db.create_career_graph_schema()
        
        # Roles
        roles = [
            {
                'id': 'cse-student',
                'title': 'Fourth-year CSE student',
                'industry': 'Technology',
                'level': 'Entry',
                'avg_salary': 0,
                'growth_rate': 0.0,
                'demand_score': 70
            },
            {
                'id': 'swe-junior',
                'title': 'Junior Software Engineer',
                'industry': 'Technology',
                'level': 'Junior',
                'avg_salary': 70000,
                'growth_rate': 0.15,
                'demand_score': 80
            },
            {
                'id': 'swe-mid',
                'title': 'Software Engineer',
                'industry': 'Technology',
                'level': 'Mid',
                'avg_salary': 95000,
                'growth_rate': 0.22,
                'demand_score': 85
            },
            {
                'id': 'swe-senior',
                'title': 'Senior Software Engineer',
                'industry': 'Technology',
                'level': 'Senior',
                'avg_salary': 130000,
                'growth_rate': 0.18,
                'demand_score': 90
            },
            {
                'id': 'data-scientist',
                'title': 'Data Scientist',
                'industry': 'Technology',
                'level': 'Mid',
                'avg_salary': 110000,
                'growth_rate': 0.25,
                'demand_score': 95
            }
        ]
        
        for role in roles:
            print(f"Adding role: {role['title']}")
            graph_db.add_role(role)
            
        # Transitions
        transitions = [
            ('cse-student', 'swe-junior', {'avg_months': 0, 'difficulty': 2, 'success_rate': 0.9, 'common_path': True}),
            ('swe-junior', 'swe-mid', {'avg_months': 24, 'difficulty': 3, 'success_rate': 0.8, 'common_path': True}),
            ('swe-mid', 'swe-senior', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.65, 'common_path': True}),
            ('swe-mid', 'data-scientist', {'avg_months': 12, 'difficulty': 7, 'success_rate': 0.4, 'common_path': False})
        ]
        
        for from_id, to_id, data in transitions:
            print(f"Adding transition: {from_id} -> {to_id}")
            graph_db.add_transition(from_id, to_id, data)
            
        # Skills
        skills = [
            ('cse-student', 'Java', 3, 'high'),
            ('cse-student', 'Python', 3, 'high'),
            ('swe-junior', 'Python', 3, 'high'),
            ('swe-mid', 'Python', 4, 'critical'),
            ('swe-mid', 'System Design', 3, 'high'),
            ('swe-senior', 'System Design', 5, 'critical'),
            ('data-scientist', 'Python', 5, 'critical'),
            ('data-scientist', 'Machine Learning', 4, 'critical')
        ]
        
        for role_id, skill_name, proficiency, importance in skills:
            skill_id = skill_name.lower().replace(' ', '-')
            print(f"Adding skill requirement: {role_id} requires {skill_name}")
            graph_db.add_skill_requirement(role_id, skill_id, proficiency, importance, skill_name=skill_name)
            
    finally:
        graph_db.close()
        print("Seeding complete.")

if __name__ == "__main__":
    seed_careers()
