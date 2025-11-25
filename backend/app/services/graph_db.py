"""
Career path finding using Neo4j graph database
"""

import google.generativeai as genai
from neo4j import GraphDatabase
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class CareerPath:
    roles: List[str]
    total_months: int
    avg_difficulty: float
    salary_growth: int
    required_skills: List[str]

class CareerGraphDB:
    def __init__(self, uri: str, user: str, password: str, google_api_key: Optional[str] = None):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.google_api_key = google_api_key
    
    def close(self):
        self.driver.close()
    
    def create_career_graph_schema(self):
        """Initialize career graph schema"""
        with self.driver.session() as session:
            # Create constraints
            session.run("""
                CREATE CONSTRAINT role_id IF NOT EXISTS
                FOR (r:Role) REQUIRE r.id IS UNIQUE
            """)
            
            session.run("""
                CREATE CONSTRAINT skill_id IF NOT EXISTS
                FOR (s:Skill) REQUIRE s.id IS UNIQUE
            """)
    
    def add_role(self, role_data: Dict):
        """Add a career role to graph"""
        with self.driver.session() as session:
            session.run("""
                MERGE (r:Role {id: $id})
                SET r.title = $title,
                    r.industry = $industry,
                    r.level = $level,
                    r.avg_salary = $avg_salary,
                    r.growth_rate = $growth_rate,
                    r.demand_score = $demand_score
            """, **role_data)
    
    def add_transition(self, from_role_id: str, to_role_id: str, 
                      transition_data: Dict):
        """Add career transition relationship"""
        with self.driver.session() as session:
            session.run("""
                MATCH (from:Role {id: $from_id})
                MATCH (to:Role {id: $to_id})
                MERGE (from)-[t:TRANSITIONS_TO]->(to)
                SET t.avg_months = $avg_months,
                    t.difficulty = $difficulty,
                    t.success_rate = $success_rate,
                    t.common_path = $common_path
            """, from_id=from_role_id, to_id=to_role_id, **transition_data)
    
    def add_skill_requirement(self, role_id: str, skill_id: str, 
                            proficiency: int, importance: str, skill_name: Optional[str] = None):
        """Link role to required skill"""
        with self.driver.session() as session:
            session.run("""
                MATCH (r:Role {id: $role_id})
                MERGE (s:Skill {id: $skill_id})
                ON CREATE SET s.name = $skill_name
                MERGE (r)-[req:REQUIRES_SKILL]->(s)
                SET req.proficiency = $proficiency,
                    req.importance = $importance
            """, role_id=role_id, skill_id=skill_id, 
                proficiency=proficiency, importance=importance, skill_name=skill_name or skill_id)
    
    def find_career_paths(self, current_role: str, target_role: Optional[str] = None,
                         max_hops: int = 4) -> List[CareerPath]:
        """Find possible career paths"""
        
        # Try AI-powered role matching if exact match might fail
        matched_current = self._match_role_with_ai(current_role)
        if matched_current:
            current_role = matched_current
        
        if target_role:
            matched_target = self._match_role_with_ai(target_role)
            if matched_target:
                target_role = matched_target
        
        with self.driver.session() as session:
            if target_role:
                # Find paths to specific target
                query = f"""
                    MATCH path = allShortestPaths(
                        (current:Role {{title: $current}})-[:TRANSITIONS_TO*1..{max_hops}]->(target:Role {{title: $target}})
                    )
                    WITH path, relationships(path) as rels, nodes(path) as roles
                    RETURN 
                        [r in roles | r.title] as role_titles,
                        reduce(months = 0, rel in rels | months + rel.avg_months) as total_months,
                        reduce(diff = 0, rel in rels | diff + rel.difficulty) / size(rels) as avg_difficulty,
                        roles[-1].avg_salary - roles[0].avg_salary as salary_growth
                    ORDER BY total_months, avg_difficulty
                    LIMIT 10
                """
                result = session.run(query, current=current_role, target=target_role)
            else:
                # Find all possible paths from current role
                query = f"""
                    MATCH path = (current:Role {{title: $current}})-[:TRANSITIONS_TO*1..{max_hops}]->(target:Role)
                    WITH path, relationships(path) as rels, nodes(path) as roles
                    WHERE size(roles) >= 2
                    RETURN DISTINCT
                        [r in roles | r.title] as role_titles,
                        reduce(months = 0, rel in rels | months + rel.avg_months) as total_months,
                        reduce(diff = 0, rel in rels | diff + rel.difficulty) / size(rels) as avg_difficulty,
                        roles[-1].avg_salary - roles[0].avg_salary as salary_growth
                    ORDER BY salary_growth DESC, total_months ASC
                    LIMIT 20
                """
                result = session.run(query, current=current_role)
            
            paths = []
            for record in result:
                # Get required skills for target role
                target = record['role_titles'][-1]
                skills = self._get_role_skills(target)
                
                paths.append(CareerPath(
                    roles=record['role_titles'],
                    total_months=record['total_months'],
                    avg_difficulty=record['avg_difficulty'],
                    salary_growth=record['salary_growth'],
                    required_skills=skills
                ))
            
            return paths
    
    def _get_all_roles(self) -> List[str]:
        """Get all role titles from database"""
        with self.driver.session() as session:
            result = session.run("MATCH (r:Role) RETURN r.title as title")
            return [record['title'] for record in result]
    
    def _match_role_with_ai(self, user_role: str) -> Optional[str]:
        """Use Gemini to find the best matching role from database"""
        try:
            if not self.google_api_key:
                print(f"[DEBUG] No GOOGLE_API_KEY found, skipping AI matching")
                return None
            
            available_roles = self._get_all_roles()
            if not available_roles:
                print(f"[DEBUG] No roles found in database")
                return None
            
            print(f"[DEBUG] AI matching '{user_role}' against {len(available_roles)} database roles: {available_roles}")
            
            genai.configure(api_key=self.google_api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            prompt = f"""Given these career roles from a database:
{chr(10).join(f'- {role}' for role in available_roles)}

Which ONE role best matches this user input: "{user_role}"?

Return ONLY the exact role name from the list above, nothing else. If no good match exists, return "NONE"."""
            
            response = model.generate_content(prompt)
            matched_role = response.text.strip()
            
            print(f"[DEBUG] AI matched '{user_role}' -> '{matched_role}'")
            
            if matched_role in available_roles:
                return matched_role
            return None
        except Exception as e:
            print(f"[DEBUG] AI role matching failed: {e}")
            return None
    
    def _get_role_skills(self, role_title: str) -> List[str]:
        """Get required skills for a role"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r:Role {title: $title})-[req:REQUIRES_SKILL]->(s:Skill)
                WHERE req.importance IN ['high', 'critical']
                RETURN s.name as skill
                ORDER BY req.proficiency DESC
            """, title=role_title)
            
            return [record['skill'] for record in result]

if __name__ == "__main__":
    # Usage
    graph_db = CareerGraphDB(
        uri="neo4j://127.0.0.1:7687",
        user="neo4j",
        password="12345678"
    )

    # Add roles
    graph_db.add_role({
        'id': 'swe-mid',
        'title': 'Software Engineer',
        'industry': 'Technology',
        'level': 'Mid',
        'avg_salary': 95000,
        'growth_rate': 0.22,
        'demand_score': 85
    })

    # Add transition
    graph_db.add_transition(
        'swe-mid', 'swe-senior',
        {
            'avg_months': 24,
            'difficulty': 5,
            'success_rate': 0.65,
            'common_path': True
        }
    )

    # Find paths
    paths = graph_db.find_career_paths('Software Engineer', 'Engineering Manager')
