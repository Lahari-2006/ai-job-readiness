"""
Skill Intelligence Layer
=======================
This is the core intelligence module of the system.

Responsibilities:
  1. Maintain a curated taxonomy of technical skills organized by category.
  2. Filter raw Comprehend key phrases to identify genuine technical skills.
  3. Categorize identified skills (languages, frameworks, tools, cloud, databases, concepts).

The taxonomy is intentionally comprehensive yet expandable — add new skills here
as the tech landscape evolves without changing any other module.
"""

from typing import Dict, List, Set
from app.models.schemas import SkillCategories

# ── Master Skill Taxonomy ──────────────────────────────────────────────────────
# Each category maps to a set of lowercase skill names / aliases.
# Aliases allow matching "js" → "javascript", "k8s" → "kubernetes", etc.

SKILL_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "languages": {
        "python": ["python", "py"],
        "javascript": ["javascript", "js", "node.js", "nodejs", "node"],
        "typescript": ["typescript", "ts"],
        "java": ["java", "java 8", "java 11", "java 17"],
        "kotlin": ["kotlin"],
        "swift": ["swift"],
        "go": ["golang", "go language", "go lang"],
        "rust": ["rust"],
        "c++": ["c++", "cpp", "c plus plus"],
        "c#": ["c#", "csharp", "c sharp"],
        "php": ["php"],
        "ruby": ["ruby", "ruby on rails"],
        "scala": ["scala"],
        "r": ["r language", "r programming"],
        "sql": ["sql", "mysql", "postgresql", "pl/sql", "t-sql"],
        "bash": ["bash", "shell script", "bash scripting"],
        "html": ["html", "html5"],
        "css": ["css", "css3", "sass", "scss", "less"],
        "dart": ["dart", "flutter"],
    },
    "frameworks": {
        "react": ["react", "react.js", "reactjs"],
        "angular": ["angular", "angularjs"],
        "vue": ["vue", "vue.js", "vuejs"],
        "next.js": ["next.js", "nextjs"],
        "django": ["django"],
        "flask": ["flask"],
        "fastapi": ["fastapi", "fast api"],
        "spring": ["spring", "spring boot", "spring mvc", "spring framework"],
        "express": ["express", "express.js", "expressjs"],
        "nestjs": ["nestjs", "nest.js"],
        "laravel": ["laravel"],
        "rails": ["rails", "ruby on rails"],
        "tensorflow": ["tensorflow", "tf"],
        "pytorch": ["pytorch", "torch"],
        "keras": ["keras"],
        "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
        "pandas": ["pandas"],
        "numpy": ["numpy"],
        "celery": ["celery"],
        "graphql": ["graphql"],
        "rest": ["rest", "restful", "rest api"],
        "grpc": ["grpc"],
        "redux": ["redux"],
        "tailwind": ["tailwind", "tailwind css"],
        "bootstrap": ["bootstrap"],
        "junit": ["junit", "pytest", "jest", "mocha"],
    },
    "tools": {
        "git": ["git", "github", "gitlab", "bitbucket"],
        "docker": ["docker", "dockerfile", "containerization"],
        "kubernetes": ["kubernetes", "k8s", "kubectl", "helm"],
        "jenkins": ["jenkins", "jenkins pipeline"],
        "github actions": ["github actions", "gh actions"],
        "circleci": ["circleci"],
        "ansible": ["ansible"],
        "terraform": ["terraform", "terraform cloud"],
        "nginx": ["nginx"],
        "apache": ["apache"],
        "linux": ["linux", "ubuntu", "centos", "debian"],
        "jira": ["jira", "jira board"],
        "confluence": ["confluence"],
        "postman": ["postman"],
        "swagger": ["swagger", "openapi"],
        "elasticsearch": ["elasticsearch", "elk", "elk stack"],
        "kafka": ["kafka", "apache kafka"],
        "rabbitmq": ["rabbitmq", "message queue"],
        "prometheus": ["prometheus"],
        "grafana": ["grafana"],
        "sonarqube": ["sonarqube"],
        "webpack": ["webpack"],
        "vite": ["vite"],
        "figma": ["figma"],
    },
    "cloud": {
        "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "rds",
                "cloudformation", "ecs", "eks", "cloudwatch", "sns", "sqs",
                "api gateway", "aws comprehend", "aws s3", "aws lambda"],
        "azure": ["azure", "microsoft azure", "azure devops", "azure functions"],
        "gcp": ["gcp", "google cloud", "google cloud platform", "bigquery",
                "cloud run", "cloud functions"],
        "heroku": ["heroku"],
        "vercel": ["vercel"],
        "netlify": ["netlify"],
        "digitalocean": ["digitalocean"],
        "cloudflare": ["cloudflare"],
    },
    "databases": {
        "postgresql": ["postgresql", "postgres"],
        "mysql": ["mysql"],
        "mongodb": ["mongodb", "mongo"],
        "redis": ["redis"],
        "sqlite": ["sqlite"],
        "cassandra": ["cassandra", "apache cassandra"],
        "dynamodb": ["dynamodb", "aws dynamodb"],
        "firebase": ["firebase", "firestore"],
        "neo4j": ["neo4j"],
        "oracle": ["oracle", "oracle db"],
        "ms sql server": ["sql server", "mssql", "ms sql"],
        "clickhouse": ["clickhouse"],
        "snowflake": ["snowflake"],
    },
    "concepts": {
        "machine learning": ["machine learning", "ml"],
        "deep learning": ["deep learning", "dl"],
        "nlp": ["nlp", "natural language processing"],
        "computer vision": ["computer vision", "cv", "image recognition"],
        "data science": ["data science"],
        "data engineering": ["data engineering", "etl", "data pipeline"],
        "devops": ["devops", "dev ops"],
        "mlops": ["mlops"],
        "ci/cd": ["ci/cd", "continuous integration", "continuous deployment", "cicd"],
        "microservices": ["microservices", "microservice architecture"],
        "system design": ["system design"],
        "api design": ["api design", "api development"],
        "agile": ["agile", "scrum", "kanban", "sprint"],
        "tdd": ["tdd", "test driven development", "unit testing"],
        "oop": ["oop", "object oriented programming", "object-oriented"],
        "functional programming": ["functional programming"],
        "data structures": ["data structures", "algorithms", "dsa"],
        "cloud computing": ["cloud computing"],
        "security": ["security", "cybersecurity", "owasp", "authentication", "oauth"],
        "blockchain": ["blockchain", "web3", "solidity"],
        "embedded systems": ["embedded systems", "iot", "arduino", "raspberry pi"],
    },
}

# Build a flat lookup: alias → (canonical_name, category)
_ALIAS_LOOKUP: Dict[str, tuple] = {}
for _category, _skills in SKILL_TAXONOMY.items():
    for _canonical, _aliases in _skills.items():
        for _alias in _aliases:
            _ALIAS_LOOKUP[_alias.lower()] = (_canonical, _category)


def identify_skills(phrases: List[str]) -> Set[str]:
    """
    From a list of raw key phrases (from Comprehend), identify which ones
    are known technical skills by matching against the taxonomy.

    Args:
        phrases: Raw key phrases from AWS Comprehend

    Returns:
        Set of canonical skill names found in the phrases
    """
    found_skills: Set[str] = set()

    for phrase in phrases:
        phrase_lower = phrase.lower().strip()

        # Direct alias match
        if phrase_lower in _ALIAS_LOOKUP:
            canonical, _ = _ALIAS_LOOKUP[phrase_lower]
            found_skills.add(canonical)
            continue

        # Substring match — catch phrases like "experience with python 3.9"
        for alias, (canonical, _) in _ALIAS_LOOKUP.items():
            if alias in phrase_lower:
                found_skills.add(canonical)
                break

    return found_skills


def categorize_skills(skills: Set[str]) -> SkillCategories:
    """
    Group a set of canonical skill names into their respective categories.

    Args:
        skills: Set of canonical skill names

    Returns:
        SkillCategories object with filled lists per category
    """
    categories = SkillCategories()

    for skill in skills:
        # Find which category this skill belongs to
        for category, skill_dict in SKILL_TAXONOMY.items():
            if skill in skill_dict:
                getattr(categories, category).append(skill)
                break

    return categories


def fallback_skill_extraction(text: str) -> Set[str]:
    """
    Fallback skill extraction using direct keyword scanning.
    Scans every alias in the taxonomy against the full text.
    """
    found_skills: Set[str] = set()
    text_lower = text.lower()

    for alias, (canonical, _) in _ALIAS_LOOKUP.items():
        # Check if alias appears anywhere in the text
        if alias in text_lower:
            found_skills.add(canonical)

    return found_skills