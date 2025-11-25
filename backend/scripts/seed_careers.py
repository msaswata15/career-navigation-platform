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
            # Entry Level & Internships
            {'id': 'intern-swe', 'title': 'Software Developer Intern', 'industry': 'Technology', 'level': 'Intern', 'avg_salary': 20000, 'growth_rate': 0.0, 'demand_score': 65},
            {'id': 'cse-student', 'title': 'Fourth-year CSE student', 'industry': 'Technology', 'level': 'Entry', 'avg_salary': 0, 'growth_rate': 0.0, 'demand_score': 70},
            {'id': 'qa-intern', 'title': 'QA Tester Intern', 'industry': 'Technology', 'level': 'Intern', 'avg_salary': 18000, 'growth_rate': 0.0, 'demand_score': 60},
            {'id': 'data-intern', 'title': 'Data Analyst Intern', 'industry': 'Technology', 'level': 'Intern', 'avg_salary': 22000, 'growth_rate': 0.0, 'demand_score': 70},
            {'id': 'ui-intern', 'title': 'UI/UX Design Intern', 'industry': 'Technology', 'level': 'Intern', 'avg_salary': 19000, 'growth_rate': 0.0, 'demand_score': 62},
            
            # Junior Roles
            {'id': 'swe-junior', 'title': 'Junior Software Engineer', 'industry': 'Technology', 'level': 'Junior', 'avg_salary': 70000, 'growth_rate': 0.15, 'demand_score': 80},
            {'id': 'frontend-junior', 'title': 'Junior Frontend Developer', 'industry': 'Technology', 'level': 'Junior', 'avg_salary': 68000, 'growth_rate': 0.16, 'demand_score': 82},
            {'id': 'backend-junior', 'title': 'Junior Backend Developer', 'industry': 'Technology', 'level': 'Junior', 'avg_salary': 72000, 'growth_rate': 0.17, 'demand_score': 83},
            {'id': 'fullstack-junior', 'title': 'Junior Full Stack Developer', 'industry': 'Technology', 'level': 'Junior', 'avg_salary': 75000, 'growth_rate': 0.18, 'demand_score': 85},
            {'id': 'mobile-junior', 'title': 'Junior Mobile Developer', 'industry': 'Technology', 'level': 'Junior', 'avg_salary': 71000, 'growth_rate': 0.16, 'demand_score': 78},
            {'id': 'qa-junior', 'title': 'Junior QA Engineer', 'industry': 'Technology', 'level': 'Junior', 'avg_salary': 62000, 'growth_rate': 0.14, 'demand_score': 75},
            {'id': 'devops-junior', 'title': 'Junior DevOps Engineer', 'industry': 'Technology', 'level': 'Junior', 'avg_salary': 73000, 'growth_rate': 0.19, 'demand_score': 80},
            {'id': 'data-analyst-junior', 'title': 'Junior Data Analyst', 'industry': 'Technology', 'level': 'Junior', 'avg_salary': 65000, 'growth_rate': 0.15, 'demand_score': 77},
            
            # Mid-Level Roles
            {'id': 'swe-mid', 'title': 'Software Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 95000, 'growth_rate': 0.22, 'demand_score': 85},
            {'id': 'frontend-mid', 'title': 'Frontend Developer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 92000, 'growth_rate': 0.20, 'demand_score': 84},
            {'id': 'backend-mid', 'title': 'Backend Developer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 98000, 'growth_rate': 0.21, 'demand_score': 86},
            {'id': 'fullstack-mid', 'title': 'Full Stack Developer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 100000, 'growth_rate': 0.23, 'demand_score': 88},
            {'id': 'mobile-mid', 'title': 'Mobile Developer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 96000, 'growth_rate': 0.20, 'demand_score': 82},
            {'id': 'qa-mid', 'title': 'QA Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 82000, 'growth_rate': 0.17, 'demand_score': 78},
            {'id': 'devops-mid', 'title': 'DevOps Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 105000, 'growth_rate': 0.24, 'demand_score': 90},
            {'id': 'data-engineer', 'title': 'Data Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 110000, 'growth_rate': 0.25, 'demand_score': 92},
            {'id': 'data-scientist', 'title': 'Data Scientist', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 115000, 'growth_rate': 0.26, 'demand_score': 95},
            {'id': 'ml-engineer', 'title': 'Machine Learning Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 120000, 'growth_rate': 0.28, 'demand_score': 94},
            {'id': 'security-engineer', 'title': 'Security Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 108000, 'growth_rate': 0.23, 'demand_score': 87},
            {'id': 'cloud-engineer', 'title': 'Cloud Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 106000, 'growth_rate': 0.24, 'demand_score': 89},
            {'id': 'ui-designer', 'title': 'UI/UX Designer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 85000, 'growth_rate': 0.18, 'demand_score': 80},
            {'id': 'product-designer', 'title': 'Product Designer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 95000, 'growth_rate': 0.20, 'demand_score': 83},
            
            # Senior Roles
            {'id': 'swe-senior', 'title': 'Senior Software Engineer', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 130000, 'growth_rate': 0.18, 'demand_score': 90},
            {'id': 'frontend-senior', 'title': 'Senior Frontend Developer', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 125000, 'growth_rate': 0.17, 'demand_score': 88},
            {'id': 'backend-senior', 'title': 'Senior Backend Developer', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 135000, 'growth_rate': 0.19, 'demand_score': 91},
            {'id': 'fullstack-senior', 'title': 'Senior Full Stack Developer', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 140000, 'growth_rate': 0.20, 'demand_score': 92},
            {'id': 'mobile-senior', 'title': 'Senior Mobile Developer', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 128000, 'growth_rate': 0.17, 'demand_score': 86},
            {'id': 'devops-senior', 'title': 'Senior DevOps Engineer', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 145000, 'growth_rate': 0.21, 'demand_score': 93},
            {'id': 'data-scientist-senior', 'title': 'Senior Data Scientist', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 150000, 'growth_rate': 0.22, 'demand_score': 96},
            {'id': 'ml-engineer-senior', 'title': 'Senior ML Engineer', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 155000, 'growth_rate': 0.24, 'demand_score': 95},
            {'id': 'security-engineer-senior', 'title': 'Senior Security Engineer', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 142000, 'growth_rate': 0.20, 'demand_score': 90},
            {'id': 'cloud-architect', 'title': 'Cloud Architect', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 148000, 'growth_rate': 0.21, 'demand_score': 92},
            
            # Lead & Staff Roles
            {'id': 'tech-lead', 'title': 'Tech Lead', 'industry': 'Technology', 'level': 'Lead', 'avg_salary': 160000, 'growth_rate': 0.16, 'demand_score': 88},
            {'id': 'staff-engineer', 'title': 'Staff Engineer', 'industry': 'Technology', 'level': 'Staff', 'avg_salary': 170000, 'growth_rate': 0.17, 'demand_score': 90},
            {'id': 'principal-engineer', 'title': 'Principal Engineer', 'industry': 'Technology', 'level': 'Principal', 'avg_salary': 190000, 'growth_rate': 0.15, 'demand_score': 85},
            {'id': 'architect', 'title': 'Solutions Architect', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 165000, 'growth_rate': 0.18, 'demand_score': 89},
            {'id': 'data-architect', 'title': 'Data Architect', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 162000, 'growth_rate': 0.19, 'demand_score': 87},
            
            # Management Roles
            {'id': 'eng-manager', 'title': 'Engineering Manager', 'industry': 'Technology', 'level': 'Manager', 'avg_salary': 155000, 'growth_rate': 0.16, 'demand_score': 84},
            {'id': 'senior-eng-manager', 'title': 'Senior Engineering Manager', 'industry': 'Technology', 'level': 'Manager', 'avg_salary': 180000, 'growth_rate': 0.14, 'demand_score': 82},
            {'id': 'director-eng', 'title': 'Director of Engineering', 'industry': 'Technology', 'level': 'Director', 'avg_salary': 210000, 'growth_rate': 0.12, 'demand_score': 78},
            {'id': 'vp-eng', 'title': 'VP of Engineering', 'industry': 'Technology', 'level': 'Executive', 'avg_salary': 280000, 'growth_rate': 0.10, 'demand_score': 70},
            {'id': 'cto', 'title': 'Chief Technology Officer', 'industry': 'Technology', 'level': 'Executive', 'avg_salary': 350000, 'growth_rate': 0.08, 'demand_score': 65},
            
            # Product Management
            {'id': 'product-analyst', 'title': 'Product Analyst', 'industry': 'Technology', 'level': 'Junior', 'avg_salary': 72000, 'growth_rate': 0.18, 'demand_score': 76},
            {'id': 'product-manager', 'title': 'Product Manager', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 115000, 'growth_rate': 0.22, 'demand_score': 88},
            {'id': 'senior-product-manager', 'title': 'Senior Product Manager', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 145000, 'growth_rate': 0.19, 'demand_score': 86},
            {'id': 'product-lead', 'title': 'Product Lead', 'industry': 'Technology', 'level': 'Lead', 'avg_salary': 165000, 'growth_rate': 0.16, 'demand_score': 82},
            {'id': 'director-product', 'title': 'Director of Product', 'industry': 'Technology', 'level': 'Director', 'avg_salary': 195000, 'growth_rate': 0.14, 'demand_score': 80},
            {'id': 'vp-product', 'title': 'VP of Product', 'industry': 'Technology', 'level': 'Executive', 'avg_salary': 260000, 'growth_rate': 0.11, 'demand_score': 72},
            {'id': 'cpo', 'title': 'Chief Product Officer', 'industry': 'Technology', 'level': 'Executive', 'avg_salary': 320000, 'growth_rate': 0.09, 'demand_score': 68},
            
            # Specialized Roles
            {'id': 'blockchain-developer', 'title': 'Blockchain Developer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 125000, 'growth_rate': 0.30, 'demand_score': 75},
            {'id': 'ai-researcher', 'title': 'AI Researcher', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 160000, 'growth_rate': 0.28, 'demand_score': 91},
            {'id': 'robotics-engineer', 'title': 'Robotics Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 105000, 'growth_rate': 0.22, 'demand_score': 73},
            {'id': 'game-developer', 'title': 'Game Developer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 88000, 'growth_rate': 0.17, 'demand_score': 70},
            {'id': 'embedded-engineer', 'title': 'Embedded Systems Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 98000, 'growth_rate': 0.19, 'demand_score': 74},
            {'id': 'ios-developer', 'title': 'iOS Developer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 102000, 'growth_rate': 0.19, 'demand_score': 81},
            {'id': 'android-developer', 'title': 'Android Developer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 100000, 'growth_rate': 0.19, 'demand_score': 82},
            {'id': 'react-native-dev', 'title': 'React Native Developer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 96000, 'growth_rate': 0.20, 'demand_score': 79},
            {'id': 'flutter-developer', 'title': 'Flutter Developer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 94000, 'growth_rate': 0.21, 'demand_score': 77},
            
            # Business & Analytics
            {'id': 'business-analyst', 'title': 'Business Analyst', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 78000, 'growth_rate': 0.15, 'demand_score': 79},
            {'id': 'senior-business-analyst', 'title': 'Senior Business Analyst', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 102000, 'growth_rate': 0.14, 'demand_score': 77},
            {'id': 'bi-analyst', 'title': 'BI Analyst', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 82000, 'growth_rate': 0.17, 'demand_score': 80},
            {'id': 'bi-developer', 'title': 'BI Developer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 92000, 'growth_rate': 0.19, 'demand_score': 82},
            
            # Support & Operations
            {'id': 'tech-support', 'title': 'Technical Support Specialist', 'industry': 'Technology', 'level': 'Junior', 'avg_salary': 52000, 'growth_rate': 0.12, 'demand_score': 68},
            {'id': 'systems-admin', 'title': 'Systems Administrator', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 75000, 'growth_rate': 0.15, 'demand_score': 74},
            {'id': 'network-engineer', 'title': 'Network Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 85000, 'growth_rate': 0.16, 'demand_score': 76},
            {'id': 'database-admin', 'title': 'Database Administrator', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 92000, 'growth_rate': 0.17, 'demand_score': 78},
            {'id': 'site-reliability-engineer', 'title': 'Site Reliability Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 118000, 'growth_rate': 0.23, 'demand_score': 91},
            
            # Specialized Data Roles
            {'id': 'data-analyst', 'title': 'Data Analyst', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 80000, 'growth_rate': 0.18, 'demand_score': 83},
            {'id': 'senior-data-analyst', 'title': 'Senior Data Analyst', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 105000, 'growth_rate': 0.17, 'demand_score': 81},
            {'id': 'analytics-engineer', 'title': 'Analytics Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 95000, 'growth_rate': 0.20, 'demand_score': 84},
            {'id': 'nlp-engineer', 'title': 'NLP Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 122000, 'growth_rate': 0.27, 'demand_score': 89},
            {'id': 'computer-vision-engineer', 'title': 'Computer Vision Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 125000, 'growth_rate': 0.28, 'demand_score': 88},
            
            # Quality & Testing
            {'id': 'qa-automation', 'title': 'QA Automation Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 88000, 'growth_rate': 0.18, 'demand_score': 80},
            {'id': 'sdet', 'title': 'Software Development Engineer in Test', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 95000, 'growth_rate': 0.19, 'demand_score': 82},
            {'id': 'senior-qa', 'title': 'Senior QA Engineer', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 110000, 'growth_rate': 0.16, 'demand_score': 78},
            {'id': 'qa-lead', 'title': 'QA Lead', 'industry': 'Technology', 'level': 'Lead', 'avg_salary': 125000, 'growth_rate': 0.15, 'demand_score': 75},
            
            # Design Roles
            {'id': 'graphic-designer', 'title': 'Graphic Designer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 62000, 'growth_rate': 0.13, 'demand_score': 71},
            {'id': 'senior-ui-designer', 'title': 'Senior UI/UX Designer', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 115000, 'growth_rate': 0.16, 'demand_score': 82},
            {'id': 'ux-researcher', 'title': 'UX Researcher', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 90000, 'growth_rate': 0.17, 'demand_score': 78},
            {'id': 'design-lead', 'title': 'Design Lead', 'industry': 'Technology', 'level': 'Lead', 'avg_salary': 135000, 'growth_rate': 0.15, 'demand_score': 76},
            
            # Emerging Tech
            {'id': 'ar-vr-developer', 'title': 'AR/VR Developer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 105000, 'growth_rate': 0.25, 'demand_score': 72},
            {'id': 'quantum-computing', 'title': 'Quantum Computing Engineer', 'industry': 'Technology', 'level': 'Senior', 'avg_salary': 145000, 'growth_rate': 0.32, 'demand_score': 68},
            {'id': 'iot-engineer', 'title': 'IoT Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 98000, 'growth_rate': 0.21, 'demand_score': 74},
            {'id': 'edge-computing', 'title': 'Edge Computing Engineer', 'industry': 'Technology', 'level': 'Mid', 'avg_salary': 102000, 'growth_rate': 0.22, 'demand_score': 73}
        ]
        
        for role in roles:
            print(f"Adding role: {role['title']}")
            graph_db.add_role(role)
            
        # Transitions - Comprehensive career progression paths
        transitions = [
            # Intern to Junior transitions
            ('intern-swe', 'swe-junior', {'avg_months': 6, 'difficulty': 2, 'success_rate': 0.85, 'common_path': True}),
            ('intern-swe', 'frontend-junior', {'avg_months': 6, 'difficulty': 2, 'success_rate': 0.75, 'common_path': True}),
            ('intern-swe', 'backend-junior', {'avg_months': 6, 'difficulty': 2, 'success_rate': 0.75, 'common_path': True}),
            ('qa-intern', 'qa-junior', {'avg_months': 6, 'difficulty': 2, 'success_rate': 0.80, 'common_path': True}),
            ('data-intern', 'data-analyst-junior', {'avg_months': 6, 'difficulty': 2, 'success_rate': 0.80, 'common_path': True}),
            ('ui-intern', 'ui-designer', {'avg_months': 6, 'difficulty': 2, 'success_rate': 0.75, 'common_path': True}),
            ('cse-student', 'swe-junior', {'avg_months': 0, 'difficulty': 2, 'success_rate': 0.9, 'common_path': True}),
            ('cse-student', 'frontend-junior', {'avg_months': 0, 'difficulty': 2, 'success_rate': 0.85, 'common_path': True}),
            ('cse-student', 'backend-junior', {'avg_months': 0, 'difficulty': 2, 'success_rate': 0.85, 'common_path': True}),
            
            # Junior to Mid transitions
            ('swe-junior', 'swe-mid', {'avg_months': 24, 'difficulty': 3, 'success_rate': 0.8, 'common_path': True}),
            ('frontend-junior', 'frontend-mid', {'avg_months': 24, 'difficulty': 3, 'success_rate': 0.75, 'common_path': True}),
            ('frontend-junior', 'fullstack-mid', {'avg_months': 30, 'difficulty': 4, 'success_rate': 0.60, 'common_path': True}),
            ('backend-junior', 'backend-mid', {'avg_months': 24, 'difficulty': 3, 'success_rate': 0.75, 'common_path': True}),
            ('backend-junior', 'fullstack-mid', {'avg_months': 30, 'difficulty': 4, 'success_rate': 0.65, 'common_path': True}),
            ('fullstack-junior', 'fullstack-mid', {'avg_months': 24, 'difficulty': 3, 'success_rate': 0.80, 'common_path': True}),
            ('mobile-junior', 'mobile-mid', {'avg_months': 24, 'difficulty': 3, 'success_rate': 0.75, 'common_path': True}),
            ('mobile-junior', 'ios-developer', {'avg_months': 18, 'difficulty': 3, 'success_rate': 0.70, 'common_path': True}),
            ('mobile-junior', 'android-developer', {'avg_months': 18, 'difficulty': 3, 'success_rate': 0.70, 'common_path': True}),
            ('qa-junior', 'qa-mid', {'avg_months': 24, 'difficulty': 3, 'success_rate': 0.75, 'common_path': True}),
            ('qa-junior', 'qa-automation', {'avg_months': 18, 'difficulty': 3, 'success_rate': 0.70, 'common_path': True}),
            ('devops-junior', 'devops-mid', {'avg_months': 24, 'difficulty': 4, 'success_rate': 0.70, 'common_path': True}),
            ('data-analyst-junior', 'data-analyst', {'avg_months': 24, 'difficulty': 3, 'success_rate': 0.75, 'common_path': True}),
            ('data-analyst-junior', 'bi-analyst', {'avg_months': 20, 'difficulty': 3, 'success_rate': 0.70, 'common_path': True}),
            
            # Mid to Senior transitions
            ('swe-mid', 'swe-senior', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.65, 'common_path': True}),
            ('frontend-mid', 'frontend-senior', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('backend-mid', 'backend-senior', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('fullstack-mid', 'fullstack-senior', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.65, 'common_path': True}),
            ('mobile-mid', 'mobile-senior', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('devops-mid', 'devops-senior', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.65, 'common_path': True}),
            ('devops-mid', 'cloud-architect', {'avg_months': 42, 'difficulty': 6, 'success_rate': 0.50, 'common_path': True}),
            ('qa-mid', 'senior-qa', {'avg_months': 36, 'difficulty': 4, 'success_rate': 0.65, 'common_path': True}),
            ('qa-automation', 'sdet', {'avg_months': 24, 'difficulty': 4, 'success_rate': 0.70, 'common_path': True}),
            
            # Data career paths
            ('data-analyst', 'senior-data-analyst', {'avg_months': 36, 'difficulty': 4, 'success_rate': 0.70, 'common_path': True}),
            ('data-analyst', 'data-engineer', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.55, 'common_path': True}),
            ('data-analyst', 'data-scientist', {'avg_months': 18, 'difficulty': 6, 'success_rate': 0.45, 'common_path': True}),
            ('data-engineer', 'data-scientist', {'avg_months': 18, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('data-scientist', 'data-scientist-senior', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.65, 'common_path': True}),
            ('data-scientist', 'ml-engineer', {'avg_months': 12, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('ml-engineer', 'ml-engineer-senior', {'avg_months': 36, 'difficulty': 6, 'success_rate': 0.60, 'common_path': True}),
            ('ml-engineer', 'ai-researcher', {'avg_months': 24, 'difficulty': 7, 'success_rate': 0.40, 'common_path': False}),
            ('swe-mid', 'data-scientist', {'avg_months': 12, 'difficulty': 7, 'success_rate': 0.40, 'common_path': False}),
            ('swe-mid', 'ml-engineer', {'avg_months': 18, 'difficulty': 6, 'success_rate': 0.45, 'common_path': False}),
            
            # Specialized engineering paths
            ('swe-mid', 'security-engineer', {'avg_months': 18, 'difficulty': 6, 'success_rate': 0.50, 'common_path': False}),
            ('swe-mid', 'cloud-engineer', {'avg_months': 12, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('security-engineer', 'security-engineer-senior', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.65, 'common_path': True}),
            ('cloud-engineer', 'cloud-architect', {'avg_months': 30, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('backend-mid', 'devops-mid', {'avg_months': 18, 'difficulty': 5, 'success_rate': 0.55, 'common_path': True}),
            ('devops-mid', 'site-reliability-engineer', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            
            # Senior to Lead/Staff transitions
            ('swe-senior', 'tech-lead', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('swe-senior', 'staff-engineer', {'avg_months': 30, 'difficulty': 6, 'success_rate': 0.50, 'common_path': True}),
            ('swe-senior', 'architect', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.55, 'common_path': True}),
            ('backend-senior', 'tech-lead', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('backend-senior', 'architect', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('fullstack-senior', 'tech-lead', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.65, 'common_path': True}),
            ('data-scientist-senior', 'staff-engineer', {'avg_months': 30, 'difficulty': 6, 'success_rate': 0.55, 'common_path': True}),
            ('data-scientist-senior', 'data-architect', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('ml-engineer-senior', 'staff-engineer', {'avg_months': 30, 'difficulty': 6, 'success_rate': 0.55, 'common_path': True}),
            ('devops-senior', 'tech-lead', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('cloud-architect', 'principal-engineer', {'avg_months': 36, 'difficulty': 6, 'success_rate': 0.45, 'common_path': True}),
            ('tech-lead', 'staff-engineer', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('staff-engineer', 'principal-engineer', {'avg_months': 36, 'difficulty': 6, 'success_rate': 0.55, 'common_path': True}),
            ('architect', 'principal-engineer', {'avg_months': 30, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            
            # Management track transitions
            ('tech-lead', 'eng-manager', {'avg_months': 18, 'difficulty': 5, 'success_rate': 0.65, 'common_path': True}),
            ('swe-senior', 'eng-manager', {'avg_months': 24, 'difficulty': 6, 'success_rate': 0.50, 'common_path': True}),
            ('eng-manager', 'senior-eng-manager', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('senior-eng-manager', 'director-eng', {'avg_months': 48, 'difficulty': 6, 'success_rate': 0.50, 'common_path': True}),
            ('director-eng', 'vp-eng', {'avg_months': 60, 'difficulty': 7, 'success_rate': 0.40, 'common_path': True}),
            ('vp-eng', 'cto', {'avg_months': 72, 'difficulty': 8, 'success_rate': 0.30, 'common_path': True}),
            ('principal-engineer', 'director-eng', {'avg_months': 36, 'difficulty': 6, 'success_rate': 0.45, 'common_path': False}),
            
            # Product Management track
            ('swe-mid', 'product-analyst', {'avg_months': 12, 'difficulty': 5, 'success_rate': 0.50, 'common_path': False}),
            ('product-analyst', 'product-manager', {'avg_months': 24, 'difficulty': 4, 'success_rate': 0.70, 'common_path': True}),
            ('product-manager', 'senior-product-manager', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('senior-product-manager', 'product-lead', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('product-lead', 'director-product', {'avg_months': 36, 'difficulty': 6, 'success_rate': 0.50, 'common_path': True}),
            ('director-product', 'vp-product', {'avg_months': 48, 'difficulty': 6, 'success_rate': 0.45, 'common_path': True}),
            ('vp-product', 'cpo', {'avg_months': 60, 'difficulty': 7, 'success_rate': 0.35, 'common_path': True}),
            
            # Design track
            ('ui-designer', 'product-designer', {'avg_months': 24, 'difficulty': 4, 'success_rate': 0.65, 'common_path': True}),
            ('ui-designer', 'senior-ui-designer', {'avg_months': 36, 'difficulty': 4, 'success_rate': 0.70, 'common_path': True}),
            ('product-designer', 'senior-ui-designer', {'avg_months': 24, 'difficulty': 4, 'success_rate': 0.70, 'common_path': True}),
            ('senior-ui-designer', 'design-lead', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.55, 'common_path': True}),
            ('ux-researcher', 'senior-ui-designer', {'avg_months': 30, 'difficulty': 4, 'success_rate': 0.60, 'common_path': True}),
            
            # Business & Analytics
            ('data-analyst', 'business-analyst', {'avg_months': 12, 'difficulty': 3, 'success_rate': 0.70, 'common_path': True}),
            ('business-analyst', 'senior-business-analyst', {'avg_months': 36, 'difficulty': 4, 'success_rate': 0.65, 'common_path': True}),
            ('senior-business-analyst', 'product-manager', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.55, 'common_path': True}),
            ('bi-analyst', 'bi-developer', {'avg_months': 24, 'difficulty': 4, 'success_rate': 0.65, 'common_path': True}),
            ('bi-developer', 'data-engineer', {'avg_months': 18, 'difficulty': 4, 'success_rate': 0.60, 'common_path': True}),
            
            # QA to Development transitions
            ('qa-automation', 'swe-mid', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.50, 'common_path': False}),
            ('sdet', 'swe-mid', {'avg_months': 18, 'difficulty': 4, 'success_rate': 0.60, 'common_path': False}),
            ('senior-qa', 'qa-lead', {'avg_months': 24, 'difficulty': 4, 'success_rate': 0.65, 'common_path': True}),
            
            # Mobile specializations
            ('mobile-mid', 'ios-developer', {'avg_months': 12, 'difficulty': 3, 'success_rate': 0.70, 'common_path': True}),
            ('mobile-mid', 'android-developer', {'avg_months': 12, 'difficulty': 3, 'success_rate': 0.70, 'common_path': True}),
            ('mobile-mid', 'react-native-dev', {'avg_months': 12, 'difficulty': 3, 'success_rate': 0.65, 'common_path': True}),
            ('mobile-mid', 'flutter-developer', {'avg_months': 12, 'difficulty': 3, 'success_rate': 0.65, 'common_path': True}),
            ('ios-developer', 'mobile-senior', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('android-developer', 'mobile-senior', {'avg_months': 36, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            
            # Specialized tech transitions
            ('swe-mid', 'blockchain-developer', {'avg_months': 12, 'difficulty': 6, 'success_rate': 0.45, 'common_path': False}),
            ('swe-mid', 'game-developer', {'avg_months': 18, 'difficulty': 5, 'success_rate': 0.50, 'common_path': False}),
            ('swe-mid', 'embedded-engineer', {'avg_months': 18, 'difficulty': 6, 'success_rate': 0.45, 'common_path': False}),
            ('ml-engineer-senior', 'nlp-engineer', {'avg_months': 12, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('ml-engineer-senior', 'computer-vision-engineer', {'avg_months': 12, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('swe-mid', 'ar-vr-developer', {'avg_months': 18, 'difficulty': 6, 'success_rate': 0.45, 'common_path': False}),
            ('swe-senior', 'robotics-engineer', {'avg_months': 24, 'difficulty': 7, 'success_rate': 0.40, 'common_path': False}),
            ('ml-engineer-senior', 'ai-researcher', {'avg_months': 24, 'difficulty': 7, 'success_rate': 0.45, 'common_path': False}),
            
            # Infrastructure & Ops
            ('tech-support', 'systems-admin', {'avg_months': 24, 'difficulty': 4, 'success_rate': 0.65, 'common_path': True}),
            ('systems-admin', 'network-engineer', {'avg_months': 24, 'difficulty': 4, 'success_rate': 0.60, 'common_path': True}),
            ('systems-admin', 'devops-junior', {'avg_months': 18, 'difficulty': 5, 'success_rate': 0.55, 'common_path': True}),
            ('network-engineer', 'security-engineer', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.50, 'common_path': True}),
            ('database-admin', 'data-engineer', {'avg_months': 24, 'difficulty': 5, 'success_rate': 0.60, 'common_path': True}),
            ('devops-mid', 'cloud-engineer', {'avg_months': 12, 'difficulty': 4, 'success_rate': 0.70, 'common_path': True})
        ]
        
        for from_id, to_id, data in transitions:
            print(f"Adding transition: {from_id} -> {to_id}")
            graph_db.add_transition(from_id, to_id, data)
            
        # Skills - Comprehensive skill requirements for all roles
        skills = [
            # Intern skills
            ('intern-swe', 'Java', 2, 'high'),
            ('intern-swe', 'JavaScript', 2, 'high'),
            ('intern-swe', 'Git', 2, 'high'),
            ('qa-intern', 'Manual Testing', 2, 'high'),
            ('data-intern', 'Excel', 2, 'high'),
            ('data-intern', 'SQL', 2, 'high'),
            ('ui-intern', 'Figma', 2, 'high'),
            
            # Student skills
            ('cse-student', 'Java', 3, 'high'),
            ('cse-student', 'Python', 3, 'high'),
            ('cse-student', 'DSA', 3, 'critical'),
            
            # Junior roles skills
            ('swe-junior', 'Python', 3, 'high'),
            ('swe-junior', 'Git', 3, 'high'),
            ('swe-junior', 'DSA', 3, 'high'),
            ('frontend-junior', 'JavaScript', 3, 'critical'),
            ('frontend-junior', 'React', 3, 'high'),
            ('frontend-junior', 'HTML/CSS', 3, 'high'),
            ('backend-junior', 'Python', 3, 'critical'),
            ('backend-junior', 'SQL', 3, 'high'),
            ('backend-junior', 'REST APIs', 3, 'high'),
            ('fullstack-junior', 'JavaScript', 3, 'critical'),
            ('fullstack-junior', 'Node.js', 3, 'high'),
            ('fullstack-junior', 'React', 3, 'high'),
            ('fullstack-junior', 'SQL', 3, 'high'),
            ('mobile-junior', 'React Native', 3, 'high'),
            ('mobile-junior', 'Mobile Development', 3, 'critical'),
            ('qa-junior', 'Test Automation', 3, 'high'),
            ('qa-junior', 'Selenium', 3, 'high'),
            ('devops-junior', 'Linux', 3, 'high'),
            ('devops-junior', 'Docker', 3, 'high'),
            ('devops-junior', 'CI/CD', 3, 'high'),
            ('data-analyst-junior', 'SQL', 3, 'critical'),
            ('data-analyst-junior', 'Excel', 3, 'high'),
            ('data-analyst-junior', 'Python', 3, 'high'),
            
            # Mid-level skills
            ('swe-mid', 'Python', 4, 'critical'),
            ('swe-mid', 'System Design', 3, 'high'),
            ('swe-mid', 'DSA', 4, 'high'),
            ('frontend-mid', 'React', 4, 'critical'),
            ('frontend-mid', 'TypeScript', 4, 'high'),
            ('frontend-mid', 'Performance Optimization', 3, 'high'),
            ('backend-mid', 'Python', 4, 'critical'),
            ('backend-mid', 'Microservices', 3, 'high'),
            ('backend-mid', 'Database Design', 4, 'high'),
            ('backend-mid', 'System Design', 3, 'high'),
            ('fullstack-mid', 'React', 4, 'critical'),
            ('fullstack-mid', 'Node.js', 4, 'critical'),
            ('fullstack-mid', 'System Design', 3, 'high'),
            ('fullstack-mid', 'Database Design', 4, 'high'),
            ('mobile-mid', 'Mobile Development', 4, 'critical'),
            ('mobile-mid', 'Performance Optimization', 3, 'high'),
            ('qa-mid', 'Test Automation', 4, 'critical'),
            ('qa-mid', 'CI/CD', 3, 'high'),
            ('devops-mid', 'Kubernetes', 4, 'critical'),
            ('devops-mid', 'AWS', 4, 'high'),
            ('devops-mid', 'Infrastructure as Code', 3, 'high'),
            ('data-engineer', 'Python', 4, 'critical'),
            ('data-engineer', 'Apache Spark', 4, 'high'),
            ('data-engineer', 'Data Pipelines', 4, 'critical'),
            ('data-scientist', 'Python', 5, 'critical'),
            ('data-scientist', 'Machine Learning', 4, 'critical'),
            ('data-scientist', 'Statistics', 4, 'high'),
            ('ml-engineer', 'Python', 5, 'critical'),
            ('ml-engineer', 'TensorFlow', 4, 'high'),
            ('ml-engineer', 'Machine Learning', 5, 'critical'),
            ('ml-engineer', 'MLOps', 3, 'high'),
            ('security-engineer', 'Cybersecurity', 4, 'critical'),
            ('security-engineer', 'Penetration Testing', 3, 'high'),
            ('cloud-engineer', 'AWS', 4, 'critical'),
            ('cloud-engineer', 'Kubernetes', 4, 'high'),
            ('cloud-engineer', 'Infrastructure as Code', 4, 'high'),
            ('ui-designer', 'Figma', 4, 'critical'),
            ('ui-designer', 'User Research', 3, 'high'),
            ('product-designer', 'UX Design', 4, 'critical'),
            ('product-designer', 'Prototyping', 4, 'high'),
            
            # Senior skills
            ('swe-senior', 'System Design', 5, 'critical'),
            ('swe-senior', 'Architecture', 4, 'high'),
            ('swe-senior', 'Mentorship', 4, 'high'),
            ('frontend-senior', 'System Design', 4, 'critical'),
            ('frontend-senior', 'Architecture', 4, 'high'),
            ('backend-senior', 'System Design', 5, 'critical'),
            ('backend-senior', 'Microservices', 5, 'high'),
            ('backend-senior', 'Architecture', 4, 'high'),
            ('fullstack-senior', 'System Design', 5, 'critical'),
            ('fullstack-senior', 'Architecture', 4, 'high'),
            ('mobile-senior', 'System Design', 4, 'high'),
            ('mobile-senior', 'Architecture', 4, 'critical'),
            ('devops-senior', 'System Design', 4, 'high'),
            ('devops-senior', 'Cloud Architecture', 5, 'critical'),
            ('data-scientist-senior', 'Machine Learning', 5, 'critical'),
            ('data-scientist-senior', 'Deep Learning', 5, 'high'),
            ('data-scientist-senior', 'Research', 4, 'high'),
            ('ml-engineer-senior', 'Machine Learning', 5, 'critical'),
            ('ml-engineer-senior', 'Deep Learning', 5, 'high'),
            ('ml-engineer-senior', 'MLOps', 5, 'high'),
            ('security-engineer-senior', 'Cybersecurity', 5, 'critical'),
            ('security-engineer-senior', 'Security Architecture', 4, 'high'),
            ('cloud-architect', 'Cloud Architecture', 5, 'critical'),
            ('cloud-architect', 'System Design', 5, 'high'),
            
            # Lead & Staff skills
            ('tech-lead', 'Leadership', 5, 'critical'),
            ('tech-lead', 'System Design', 5, 'critical'),
            ('tech-lead', 'Mentorship', 5, 'high'),
            ('staff-engineer', 'System Design', 5, 'critical'),
            ('staff-engineer', 'Architecture', 5, 'critical'),
            ('staff-engineer', 'Technical Strategy', 4, 'high'),
            ('principal-engineer', 'Architecture', 5, 'critical'),
            ('principal-engineer', 'Technical Strategy', 5, 'critical'),
            ('architect', 'System Design', 5, 'critical'),
            ('architect', 'Architecture', 5, 'critical'),
            ('data-architect', 'Data Architecture', 5, 'critical'),
            ('data-architect', 'System Design', 5, 'high'),
            
            # Management skills
            ('eng-manager', 'Leadership', 5, 'critical'),
            ('eng-manager', 'People Management', 5, 'critical'),
            ('eng-manager', 'Project Management', 4, 'high'),
            ('senior-eng-manager', 'Leadership', 5, 'critical'),
            ('senior-eng-manager', 'Strategic Planning', 5, 'high'),
            ('director-eng', 'Leadership', 5, 'critical'),
            ('director-eng', 'Strategic Planning', 5, 'critical'),
            ('vp-eng', 'Leadership', 5, 'critical'),
            ('vp-eng', 'Business Strategy', 5, 'critical'),
            ('cto', 'Leadership', 5, 'critical'),
            ('cto', 'Business Strategy', 5, 'critical'),
            ('cto', 'Technical Vision', 5, 'critical'),
            
            # Product Management skills
            ('product-analyst', 'Data Analysis', 3, 'critical'),
            ('product-analyst', 'SQL', 3, 'high'),
            ('product-manager', 'Product Strategy', 4, 'critical'),
            ('product-manager', 'Stakeholder Management', 4, 'high'),
            ('product-manager', 'Agile', 4, 'high'),
            ('senior-product-manager', 'Product Strategy', 5, 'critical'),
            ('senior-product-manager', 'Leadership', 4, 'high'),
            ('product-lead', 'Product Strategy', 5, 'critical'),
            ('product-lead', 'Leadership', 5, 'high'),
            ('director-product', 'Product Strategy', 5, 'critical'),
            ('director-product', 'Strategic Planning', 5, 'critical'),
            ('vp-product', 'Product Strategy', 5, 'critical'),
            ('vp-product', 'Business Strategy', 5, 'critical'),
            ('cpo', 'Product Strategy', 5, 'critical'),
            ('cpo', 'Business Strategy', 5, 'critical'),
            
            # Specialized roles skills
            ('blockchain-developer', 'Blockchain', 4, 'critical'),
            ('blockchain-developer', 'Solidity', 4, 'high'),
            ('ai-researcher', 'Machine Learning', 5, 'critical'),
            ('ai-researcher', 'Research', 5, 'critical'),
            ('ai-researcher', 'Deep Learning', 5, 'critical'),
            ('robotics-engineer', 'Robotics', 4, 'critical'),
            ('robotics-engineer', 'C++', 4, 'high'),
            ('game-developer', 'Game Development', 4, 'critical'),
            ('game-developer', 'Unity', 4, 'high'),
            ('embedded-engineer', 'Embedded Systems', 4, 'critical'),
            ('embedded-engineer', 'C', 4, 'critical'),
            ('ios-developer', 'Swift', 4, 'critical'),
            ('ios-developer', 'iOS Development', 4, 'critical'),
            ('android-developer', 'Kotlin', 4, 'critical'),
            ('android-developer', 'Android Development', 4, 'critical'),
            ('react-native-dev', 'React Native', 4, 'critical'),
            ('flutter-developer', 'Flutter', 4, 'critical'),
            ('flutter-developer', 'Dart', 4, 'high'),
            
            # Business & Analytics skills
            ('business-analyst', 'Business Analysis', 4, 'critical'),
            ('business-analyst', 'Requirements Gathering', 4, 'high'),
            ('senior-business-analyst', 'Business Analysis', 5, 'critical'),
            ('bi-analyst', 'Business Intelligence', 4, 'critical'),
            ('bi-analyst', 'Tableau', 4, 'high'),
            ('bi-developer', 'ETL', 4, 'critical'),
            ('bi-developer', 'SQL', 4, 'critical'),
            
            # Support & Operations skills
            ('tech-support', 'Technical Support', 3, 'critical'),
            ('systems-admin', 'Linux', 4, 'critical'),
            ('systems-admin', 'System Administration', 4, 'critical'),
            ('network-engineer', 'Networking', 4, 'critical'),
            ('network-engineer', 'TCP/IP', 4, 'high'),
            ('database-admin', 'Database Administration', 4, 'critical'),
            ('database-admin', 'SQL', 4, 'critical'),
            ('site-reliability-engineer', 'SRE', 5, 'critical'),
            ('site-reliability-engineer', 'Kubernetes', 5, 'high'),
            
            # Data roles skills
            ('data-analyst', 'SQL', 4, 'critical'),
            ('data-analyst', 'Python', 4, 'high'),
            ('data-analyst', 'Data Visualization', 4, 'high'),
            ('senior-data-analyst', 'SQL', 5, 'critical'),
            ('senior-data-analyst', 'Data Analysis', 5, 'critical'),
            ('analytics-engineer', 'SQL', 4, 'critical'),
            ('analytics-engineer', 'dbt', 4, 'high'),
            ('nlp-engineer', 'NLP', 5, 'critical'),
            ('nlp-engineer', 'Python', 5, 'critical'),
            ('computer-vision-engineer', 'Computer Vision', 5, 'critical'),
            ('computer-vision-engineer', 'PyTorch', 5, 'high'),
            
            # QA skills
            ('qa-automation', 'Test Automation', 4, 'critical'),
            ('qa-automation', 'Selenium', 4, 'high'),
            ('sdet', 'Test Automation', 5, 'critical'),
            ('sdet', 'Programming', 4, 'critical'),
            ('senior-qa', 'Test Automation', 5, 'critical'),
            ('senior-qa', 'Test Strategy', 4, 'high'),
            ('qa-lead', 'Test Strategy', 5, 'critical'),
            ('qa-lead', 'Leadership', 4, 'high'),
            
            # Design skills
            ('graphic-designer', 'Graphic Design', 4, 'critical'),
            ('graphic-designer', 'Adobe Creative Suite', 4, 'high'),
            ('senior-ui-designer', 'UX Design', 5, 'critical'),
            ('senior-ui-designer', 'Figma', 5, 'high'),
            ('ux-researcher', 'User Research', 5, 'critical'),
            ('ux-researcher', 'UX Design', 4, 'high'),
            ('design-lead', 'UX Design', 5, 'critical'),
            ('design-lead', 'Leadership', 5, 'high'),
            
            # Emerging tech skills
            ('ar-vr-developer', 'AR/VR Development', 4, 'critical'),
            ('ar-vr-developer', 'Unity', 4, 'high'),
            ('quantum-computing', 'Quantum Computing', 5, 'critical'),
            ('quantum-computing', 'Physics', 5, 'high'),
            ('iot-engineer', 'IoT', 4, 'critical'),
            ('iot-engineer', 'Embedded Systems', 4, 'high'),
            ('edge-computing', 'Edge Computing', 4, 'critical'),
            ('edge-computing', 'Distributed Systems', 4, 'high')
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
