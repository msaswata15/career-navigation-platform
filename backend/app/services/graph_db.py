"""
Career path finding using Neo4j graph database
"""

import google.generativeai as genai
from neo4j import GraphDatabase
from typing import List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class CareerPath:
    roles: List[str]
    total_months: int
    avg_difficulty: float
    salary_growth: int
    required_skills: List[str]
    transitions: List[Dict] = field(default_factory=list)  # Detailed step-by-step transition info

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
        """Find possible career paths with AI-powered role matching"""
        
        # AI-powered role matching for current role
        matched_current = self._match_role_with_ai(current_role)
        if not matched_current:
            print(f"[WARN] Could not match current role '{current_role}' to any database role")
            # Try direct match as fallback
            matched_current = current_role
        else:
            print(f"[INFO] Matched current role: '{current_role}' -> '{matched_current}'")
            current_role = matched_current
        
        # AI-powered role matching for target role
        if target_role:
            matched_target = self._match_role_with_ai(target_role)
            if not matched_target:
                print(f"[WARN] Could not match target role '{target_role}' to any database role")
                # Return empty if target can't be matched
                return []
            else:
                print(f"[INFO] Matched target role: '{target_role}' -> '{matched_target}'")
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
                        [r in roles | r.avg_salary] as role_salaries,
                        reduce(months = 0, rel in rels | months + rel.avg_months) as total_months,
                        reduce(diff = 0, rel in rels | diff + rel.difficulty) / size(rels) as avg_difficulty,
                        roles[-1].avg_salary - roles[0].avg_salary as salary_growth,
                        [rel in rels | {{avg_months: rel.avg_months, difficulty: rel.difficulty, success_rate: rel.success_rate}}] as transition_details
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
                        [r in roles | r.avg_salary] as role_salaries,
                        reduce(months = 0, rel in rels | months + rel.avg_months) as total_months,
                        reduce(diff = 0, rel in rels | diff + rel.difficulty) / size(rels) as avg_difficulty,
                        roles[-1].avg_salary - roles[0].avg_salary as salary_growth,
                        [rel in rels | {{avg_months: rel.avg_months, difficulty: rel.difficulty, success_rate: rel.success_rate}}] as transition_details
                    ORDER BY salary_growth DESC, total_months ASC
                    LIMIT 20
                """
                result = session.run(query, current=current_role)
            
            paths = []
            for record in result:
                # Get required skills for target role
                target = record['role_titles'][-1]
                skills = self._get_role_skills(target)
                
                # Build detailed transitions for each step
                transitions = []
                role_titles = record['role_titles']
                role_salaries = record['role_salaries']
                transition_details = record['transition_details']
                
                for i in range(len(role_titles) - 1):
                    from_role = role_titles[i]
                    to_role = role_titles[i + 1]
                    from_salary = role_salaries[i]
                    to_salary = role_salaries[i + 1]
                    trans_info = transition_details[i]
                    
                    # Get skills needed for the destination role of this transition
                    step_skills = self._get_role_skills(to_role)
                    
                    transitions.append({
                        'step': i + 1,
                        'from_role': from_role,
                        'to_role': to_role,
                        'duration_months': trans_info['avg_months'],
                        'difficulty': trans_info['difficulty'],
                        'success_rate': trans_info['success_rate'],
                        'salary_from': from_salary,
                        'salary_to': to_salary,
                        'salary_increase': to_salary - from_salary,
                        'required_skills': step_skills
                    })
                
                paths.append(CareerPath(
                    roles=record['role_titles'],
                    total_months=record['total_months'],
                    avg_difficulty=record['avg_difficulty'],
                    salary_growth=record['salary_growth'],
                    required_skills=skills,
                    transitions=transitions
                ))
            
            return paths
    
    def _get_all_roles(self) -> List[str]:
        """Get all role titles from database"""
        with self.driver.session() as session:
            result = session.run("MATCH (r:Role) RETURN r.title as title")
            return [record['title'] for record in result]
    
    def _match_role_with_ai(self, user_role: str) -> Optional[str]:
        """Use Gemini to find the best matching role from database - optimized for 10,000+ roles"""
        try:
            if not self.google_api_key:
                print(f"[DEBUG] No GOOGLE_API_KEY found, skipping AI matching")
                return None
            
            available_roles = self._get_all_roles()
            if not available_roles:
                print(f"[DEBUG] No roles found in database")
                return None
            
            # First try exact match (case-insensitive) - O(n) but fast
            user_role_lower = user_role.lower().strip()
            for role in available_roles:
                if role.lower() == user_role_lower:
                    print(f"[DEBUG] Exact match found: '{user_role}' -> '{role}'")
                    return role
            
            # Try partial matches with common patterns
            user_role_normalized = user_role_lower.replace('-', ' ').replace('_', ' ')
            for role in available_roles:
                role_normalized = role.lower().replace('-', ' ').replace('_', ' ')
                if user_role_normalized == role_normalized:
                    print(f"[DEBUG] Normalized match found: '{user_role}' -> '{role}'")
                    return role
            
            print(f"[DEBUG] AI matching '{user_role}' against {len(available_roles)} database roles")
            
            genai.configure(api_key=self.google_api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            # For large databases (>500 roles), use intelligent filtering
            if len(available_roles) > 500:
                # Stage 1: Smart pre-filtering using keyword extraction
                filtered_roles = self._intelligent_filter_roles(user_role, available_roles)
                print(f"[DEBUG] Pre-filtered to {len(filtered_roles)} candidate roles")
                
                if len(filtered_roles) == 0:
                    # Fallback to chunked search if filtering fails
                    return self._chunked_ai_search(user_role, available_roles, model)
                elif len(filtered_roles) == 1:
                    return filtered_roles[0]
                
                roles_to_match = filtered_roles[:100]  # Limit to top 100 for Gemini
            else:
                roles_to_match = available_roles
            
            # Stage 2: Gemini matching on filtered set
            prompt = f"""You are a career matching expert. Match the user's job title to the closest role from this list:

CANDIDATE ROLES ({len(roles_to_match)} total):
{chr(10).join(f'{i+1}. {role}' for i, role in enumerate(roles_to_match[:100]))}

USER INPUT: "{user_role}"

MATCHING RULES:
- Match job title variations (SWE=Software Engineer, Dev=Developer, Eng=Engineer)
- Match seniority levels (Intern, Junior, Mid-Senior, Senior, Lead, Staff, Principal, Manager+)
- Match specializations (Frontend, Backend, Full Stack, Mobile, Data, ML, DevOps, Cloud, Security)
- Handle abbreviations (PM=Product Manager, QA=Quality Assurance, BA=Business Analyst)
- Default vague inputs to mid-level (e.g., "devops" → "DevOps Engineer")
- Student roles map to appropriate entry positions

OUTPUT FORMAT: Return ONLY the exact role name from the numbered list above. If no match exists, return "NONE"

Examples:
"SWE intern" → "Software Developer Intern"
"senior backend dev" → "Senior Backend Developer"
"data analyst" → "Data Analyst"
"ML" → "Machine Learning Engineer"

Match:"""
            
            response = model.generate_content(prompt)
            matched_role = response.text.strip()
            
            # Clean up response
            matched_role = matched_role.replace('"', '').replace("'", '').replace('`', '').strip()
            
            # Remove numbering if present
            if '. ' in matched_role:
                parts = matched_role.split('. ')
                if parts[0].isdigit():
                    matched_role = '. '.join(parts[1:])
            
            print(f"[DEBUG] AI matched '{user_role}' -> '{matched_role}'")
            
            # Verify match is in our database (check original list, not filtered)
            if matched_role in available_roles:
                return matched_role
            
            # Case-insensitive verification
            for role in available_roles:
                if role.lower() == matched_role.lower():
                    print(f"[DEBUG] Case-insensitive match: '{matched_role}' -> '{role}'")
                    return role
            
            print(f"[WARN] AI returned '{matched_role}' but it's not in the database")
            return None
            
        except Exception as e:
            print(f"[ERROR] AI role matching failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _intelligent_filter_roles(self, user_input: str, all_roles: List[str]) -> List[str]:
        """Pre-filter roles using keyword matching for large datasets"""
        user_input_lower = user_input.lower()
        
        # Extract key terms from user input
        keywords = set(user_input_lower.replace('-', ' ').replace('_', ' ').split())
        
        # Common synonyms and variations
        synonyms = {
            'swe': ['software', 'engineer'],
            'dev': ['developer'],
            'eng': ['engineer', 'engineering'],
            'sr': ['senior'],
            'jr': ['junior'],
            'mgr': ['manager'],
            'pm': ['product', 'manager', 'project'],
            'qa': ['quality', 'assurance', 'test'],
            'ml': ['machine', 'learning'],
            'ai': ['artificial', 'intelligence'],
            'ui': ['user', 'interface'],
            'ux': ['user', 'experience'],
            'devops': ['devops', 'operations'],
            'dba': ['database', 'administrator'],
            'sre': ['reliability', 'engineer'],
            'fe': ['frontend'],
            'be': ['backend'],
            'fs': ['fullstack', 'full', 'stack']
        }
        
        # Expand keywords with synonyms
        expanded_keywords = set(keywords)
        for keyword in keywords:
            if keyword in synonyms:
                expanded_keywords.update(synonyms[keyword])
        
        # Score each role based on keyword matches
        scored_roles = []
        for role in all_roles:
            role_lower = role.lower()
            role_words = set(role_lower.replace('-', ' ').replace('_', ' ').split())
            
            # Calculate match score
            exact_matches = len(expanded_keywords & role_words)
            partial_matches = sum(1 for kw in expanded_keywords if kw in role_lower)
            
            score = exact_matches * 10 + partial_matches
            
            if score > 0:
                scored_roles.append((score, role))
        
        # Sort by score and return top candidates
        scored_roles.sort(reverse=True, key=lambda x: x[0])
        
        # Return top 50 candidates (or all if less than 50 matched)
        return [role for _, role in scored_roles[:50]] if scored_roles else []
    
    def _chunked_ai_search(self, user_role: str, all_roles: List[str], model) -> Optional[str]:
        """Search through roles in chunks for very large databases (10,000+)"""
        print(f"[DEBUG] Starting chunked search for {len(all_roles)} roles")
        
        chunk_size = 100
        best_matches = []
        
        # Process roles in chunks
        for i in range(0, len(all_roles), chunk_size):
            chunk = all_roles[i:i + chunk_size]
            
            prompt = f"""Match "{user_role}" to ONE role from this list (return exact name or "NONE"):
{chr(10).join(f'{j+1}. {role}' for j, role in enumerate(chunk))}

Match (exact name only):"""
            
            try:
                response = model.generate_content(prompt)
                match = response.text.strip().replace('"', '').replace("'", '').strip()
                
                # Clean numbering
                if '. ' in match and match.split('. ')[0].isdigit():
                    match = '. '.join(match.split('. ')[1:])
                
                if match != "NONE" and match in chunk:
                    best_matches.append(match)
                    print(f"[DEBUG] Chunk {i//chunk_size + 1}: found candidate '{match}'")
                    
            except Exception as e:
                print(f"[WARN] Chunk {i//chunk_size + 1} failed: {e}")
                continue
        
        # If multiple matches found, do final disambiguation
        if len(best_matches) > 1:
            final_prompt = f"""Which role BEST matches "{user_role}"?
{chr(10).join(f'{i+1}. {role}' for i, role in enumerate(best_matches))}

Best match (exact name):"""
            
            try:
                response = model.generate_content(final_prompt)
                final_match = response.text.strip().replace('"', '').replace("'", '').strip()
                
                if '. ' in final_match and final_match.split('. ')[0].isdigit():
                    final_match = '. '.join(final_match.split('. ')[1:])
                
                if final_match in best_matches:
                    return final_match
            except:
                pass
        
        return best_matches[0] if best_matches else None
    
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
