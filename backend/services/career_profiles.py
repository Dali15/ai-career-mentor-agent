from typing import Dict, List, Any

DEFAULT_COMPARISON_CAREERS = [
    "Frontend Developer", "Backend Developer", "Data Analyst", 
    "DevOps Engineer", "Cloud Engineer", "Mobile Developer"
]

DIMENSIONS = [
    "backend", "frontend", "data", "cloud", "devops", 
    "ai", "mobile", "database", "system_design",
    "ui_ux", "networking", "security", "testing", "machine_learning"
]

DIMENSION_WEIGHTS = {
    "backend": 1.1, "frontend": 1.0, "data": 1.1, "cloud": 1.2, "devops": 1.2,
    "ai": 1.3, "mobile": 1.0, "database": 1.1, "system_design": 1.2,
    "ui_ux": 1.0, "networking": 1.1, "security": 1.3, "testing": 1.0, "machine_learning": 1.3
}

SKILL_VECTORS = {
    "sql": {"data": 0.8, "database": 0.9, "backend": 0.6, "devops": 0.2, "cloud": 0.2},
    "python": {"backend": 0.9, "data": 0.8, "ai": 0.6, "machine_learning": 0.5},
    "react": {"frontend": 0.9, "mobile": 0.3, "backend": 0.2, "ui_ux": 0.4},
    "web apps": {"frontend": 0.6, "backend": 0.6},
    "node": {"backend": 0.9, "frontend": 0.3},
    "node.js": {"backend": 0.9, "frontend": 0.3},
    "docker": {"devops": 0.9, "cloud": 0.6, "backend": 0.4, "networking": 0.2},
    "kubernetes": {"devops": 0.9, "cloud": 0.8, "networking": 0.3},
    "aws": {"cloud": 1.0, "devops": 0.6, "networking": 0.4, "security": 0.3},
    "azure": {"cloud": 1.0, "devops": 0.6, "networking": 0.4, "security": 0.3},
    "javascript": {"frontend": 0.9, "backend": 0.4},
    "html": {"frontend": 0.8, "ui_ux": 0.6},
    "css": {"frontend": 0.8, "ui_ux": 0.7},
    "machine learning": {"ai": 1.0, "data": 0.7, "backend": 0.3, "machine_learning": 1.0},
    "data analysis": {"data": 1.0, "database": 0.6},
    "api": {"backend": 0.8, "system_design": 0.5},
    "apis": {"backend": 0.8, "system_design": 0.5},
    "system design": {"system_design": 1.0, "backend": 0.8, "cloud": 0.6},
    "mobile dev": {"mobile": 1.0, "frontend": 0.6, "ui_ux": 0.5},
    "flutter": {"mobile": 1.0, "frontend": 0.7, "ui_ux": 0.4},
}

CAREER_VECTORS = {
    "Data Analyst": {"data": 1.0, "database": 0.9, "backend": 0.4, "ai": 0.5, "machine_learning": 0.3},
    "Backend Developer": {"backend": 1.0, "database": 0.8, "system_design": 0.8, "frontend": 0.3, "testing": 0.4, "security": 0.3},
    "DevOps Engineer": {"devops": 1.0, "cloud": 0.9, "backend": 0.5, "system_design": 0.7, "networking": 0.6, "security": 0.5},
    "Cloud Engineer": {"cloud": 1.0, "devops": 0.7, "backend": 0.4, "system_design": 0.7, "networking": 0.8, "security": 0.6},
    "Mobile Developer": {"mobile": 1.0, "frontend": 0.8, "backend": 0.4, "ai": 0.2, "ui_ux": 0.5},
    "Frontend Developer": {"frontend": 1.0, "mobile": 0.5, "backend": 0.3, "ui_ux": 0.8, "testing": 0.3},
    "Full-Stack Developer": {"frontend": 0.8, "backend": 0.8, "database": 0.6, "system_design": 0.5, "ui_ux": 0.4},
    "Cybersecurity Analyst": {"devops": 0.6, "cloud": 0.7, "backend": 0.5, "system_design": 0.6, "security": 1.0, "networking": 0.9},
}

INTEREST_BOOSTS = {
    "ai": {"ai": 0.05, "data": 0.02, "cloud": 0.02, "machine_learning": 0.05},
    "web apps": {"frontend": 0.05, "backend": 0.05},
    "data analysis": {"data": 0.05, "database": 0.02},
    "data": {"data": 0.05, "database": 0.02},
    "cloud": {"cloud": 0.05, "devops": 0.02},
    "mobile": {"mobile": 0.05, "frontend": 0.02},
}
