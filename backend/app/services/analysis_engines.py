"""
Analysis Engines
================
Contains four tightly coupled engines that form the core pipeline:

  1. ComparisonEngine  — matches resume skills vs job skills
  2. ScoringEngine     — computes overall and per-category match percentages
  3. DecisionEngine    — translates score into a human-readable verdict
  4. SuggestionEngine  — converts skill gaps into actionable learning steps

Each engine is a pure function / class with no side effects,
making them individually testable and replaceable.
"""

from typing import Set, List, Dict, Tuple
from app.models.schemas import SkillCategories, MatchBreakdown
from app.core.config import settings


# ── 1. Comparison Engine ──────────────────────────────────────────────────────

class ComparisonEngine:
    """
    Compares two sets of skills and identifies matched and missing skills.
    """

    @staticmethod
    def compare(resume_skills: Set[str], job_skills: Set[str]) -> Tuple[List[str], List[str]]:
        """
        Identify which required job skills are present in the resume,
        and which are missing.

        Args:
            resume_skills: Skills extracted from resume
            job_skills: Skills extracted from job description

        Returns:
            Tuple of (matched_skills, missing_skills)
        """
        matched = sorted(resume_skills & job_skills)       # intersection
        missing = sorted(job_skills - resume_skills)       # in job but not resume
        return matched, missing


# ── 2. Scoring Engine ─────────────────────────────────────────────────────────

class ScoringEngine:
    """
    Calculates an overall match percentage and per-category breakdown.
    """

    @staticmethod
    def calculate_overall_score(
        matched_skills: List[str],
        missing_skills: List[str],
    ) -> int:
        """
        Overall score = (matched / total job skills) * 100

        Args:
            matched_skills: Skills present in both resume and job
            missing_skills: Skills required by job but absent from resume

        Returns:
            int: Score between 0 and 100
        """
        total = len(matched_skills) + len(missing_skills)
        if total == 0:
            return 0
        return int((len(matched_skills) / total) * 100)

    @staticmethod
    def calculate_category_breakdown(
        resume_cats: SkillCategories,
        job_cats: SkillCategories,
    ) -> MatchBreakdown:
        """
        Compute match percentage for each skill category independently.
        This powers the radar chart / bar chart in the UI.

        Args:
            resume_cats: Categorized resume skills
            job_cats: Categorized job description skills

        Returns:
            MatchBreakdown with per-category percentages
        """
        def category_score(resume_list: List[str], job_list: List[str]) -> float:
            if not job_list:
                return 100.0  # No requirement → not penalized
            matched = set(resume_list) & set(job_list)
            return round(len(matched) / len(job_list) * 100, 1)

        return MatchBreakdown(
            languages=category_score(resume_cats.languages, job_cats.languages),
            frameworks=category_score(resume_cats.frameworks, job_cats.frameworks),
            tools=category_score(resume_cats.tools, job_cats.tools),
            cloud=category_score(resume_cats.cloud, job_cats.cloud),
            databases=category_score(resume_cats.databases, job_cats.databases),
            concepts=category_score(resume_cats.concepts, job_cats.concepts),
        )


# ── 3. Decision Engine ────────────────────────────────────────────────────────

class DecisionEngine:
    """
    Converts a match score into a clear verdict with an emoji-ready label.
    Thresholds are configurable via settings.
    """

    DECISIONS = {
        "APPLY NOW": {
            "label": "APPLY NOW",
            "description": "Your skills strongly match the job requirements. You are a great fit!",
            "color": "green",
        },
        "IMPROVE BEFORE APPLYING": {
            "label": "IMPROVE BEFORE APPLYING",
            "description": "You have a partial match. Closing the identified skill gaps will make you competitive.",
            "color": "yellow",
        },
        "NOT SUITABLE": {
            "label": "NOT SUITABLE",
            "description": "Significant skill gaps exist. Focus on foundational skills before applying.",
            "color": "red",
        },
    }

    @classmethod
    def decide(cls, score: int) -> str:
        """
        Map a score to a decision label.

        Args:
            score: Integer 0–100

        Returns:
            str: Decision label
        """
        if score >= settings.APPLY_THRESHOLD:
            return "APPLY NOW"
        elif score >= settings.IMPROVE_THRESHOLD:
            return "IMPROVE BEFORE APPLYING"
        else:
            return "NOT SUITABLE"

    @classmethod
    def get_decision_meta(cls, decision: str) -> Dict:
        """Return full metadata for a decision label."""
        return cls.DECISIONS.get(decision, cls.DECISIONS["NOT SUITABLE"])


# ── 4. Suggestion Engine ──────────────────────────────────────────────────────

# Maps canonical skill names → actionable learning suggestions.
# This is the "intelligence" layer that converts gaps into a roadmap.
SKILL_SUGGESTIONS: Dict[str, str] = {
    # Languages
    "python": "Learn Python fundamentals via 'Python for Everybody' on Coursera or Real Python.",
    "javascript": "Master JavaScript basics via freeCodeCamp's JS Algorithms and Data Structures.",
    "typescript": "Add TypeScript to your JS projects — start with the official TypeScript Handbook.",
    "java": "Build Java skills with 'Java Programming Masterclass' on Udemy.",
    "go": "Learn Go via the official 'Tour of Go' at go.dev/tour.",
    "sql": "Practice SQL with LeetCode's database problems and Mode Analytics tutorials.",
    "rust": "Start with 'The Rust Programming Language' book (doc.rust-lang.org/book).",
    "kotlin": "Learn Kotlin via JetBrains Academy or Android Developers documentation.",

    # Frameworks
    "react": "Build 3 React projects: a to-do app, a weather dashboard, and a REST-API-driven app.",
    "fastapi": "Build a REST API using FastAPI — official docs at fastapi.tiangolo.com are excellent.",
    "django": "Complete the official Django tutorial and build a blog/CRUD application.",
    "flask": "Create a REST API with Flask and deploy it on Heroku to practice end-to-end flow.",
    "spring": "Follow the Spring Boot official guides at spring.io/guides.",
    "next.js": "Build a full-stack Next.js app using the App Router and deploy to Vercel.",
    "angular": "Complete the official Angular Tour of Heroes tutorial.",
    "vue": "Build a Vue.js SPA using Vue Router and Pinia state management.",
    "tensorflow": "Work through TensorFlow's official beginner tutorials and build a classifier.",
    "pytorch": "Complete the PyTorch 60-Minute Blitz tutorial and implement a neural network.",
    "scikit-learn": "Build ML pipelines with scikit-learn — Kaggle Intro to ML is a great start.",

    # Tools
    "docker": "Learn Docker by containerizing a personal project — 'Docker for Beginners' on Docker Hub.",
    "kubernetes": "Take 'Kubernetes for Absolute Beginners' on Udemy and deploy an app on Minikube.",
    "git": "Learn Git branching strategies at learngitbranching.js.org.",
    "jenkins": "Set up a Jenkins CI/CD pipeline for a personal project.",
    "terraform": "Follow HashiCorp's official Terraform getting-started guide on AWS.",
    "github actions": "Create a GitHub Actions workflow that runs tests and deploys automatically.",
    "kafka": "Build a producer-consumer pipeline with Apache Kafka using Kafka's quickstart guide.",
    "elasticsearch": "Set up Elasticsearch locally and practice full-text search indexing.",
    "prometheus": "Instrument a Python/Node app with Prometheus metrics and visualize in Grafana.",
    "linux": "Practice Linux commands via OverTheWire's Bandit wargame and linuxcommand.org.",

    # Cloud
    "aws": "Get AWS Cloud Practitioner certified — free prep at aws.amazon.com/training.",
    "azure": "Start with the Microsoft Azure Fundamentals (AZ-900) certification path.",
    "gcp": "Complete Google Cloud's 'Associate Cloud Engineer' learning path on Coursera.",

    # Databases
    "postgresql": "Practice PostgreSQL with 'The Art of PostgreSQL' and pgexercises.com.",
    "mongodb": "Complete MongoDB University's free M001 course.",
    "redis": "Learn Redis data structures with the official 'Redis University' free courses.",
    "mysql": "Practice MySQL via w3schools and build a relational schema for a real use case.",
    "dynamodb": "Complete AWS's official DynamoDB developer guide examples.",

    # Concepts
    "machine learning": "Start Andrew Ng's 'Machine Learning Specialization' on Coursera.",
    "deep learning": "Complete the 'Deep Learning Specialization' by deeplearning.ai on Coursera.",
    "nlp": "Work through Hugging Face's NLP course (huggingface.co/learn).",
    "devops": "Study the DevOps Roadmap at roadmap.sh/devops and implement CI/CD for a project.",
    "ci/cd": "Set up CI/CD using GitHub Actions or GitLab CI for an existing project.",
    "microservices": "Refactor a monolith project into microservices and deploy with Docker Compose.",
    "system design": "Study 'Designing Data-Intensive Applications' and practice on systemdesign.io.",
    "tdd": "Practice TDD by writing tests first for a new feature using pytest or Jest.",
    "agile": "Study Scrum methodology and practice with a personal Trello/Jira Kanban board.",
    "security": "Take OWASP Top 10 training and apply security best practices to a personal API.",
    "data science": "Complete the IBM Data Science Professional Certificate on Coursera.",
    "data engineering": "Build an ETL pipeline using Apache Airflow and PostgreSQL.",
    "computer vision": "Implement image classification using OpenCV + TensorFlow on a small dataset.",
}

DEFAULT_SUGGESTION = "Study the fundamentals of {skill} via official documentation and build a small project."


class SuggestionEngine:
    """
    Converts a list of missing skills into ranked, actionable learning suggestions.
    """

    @classmethod
    def generate_suggestions(cls, missing_skills: List[str]) -> List[str]:
        """
        Generate an ordered list of suggestions for each missing skill.

        Args:
            missing_skills: Canonical skill names that are in the job but not resume

        Returns:
            List of actionable suggestion strings (one per missing skill)
        """
        suggestions = []

        for skill in missing_skills:
            suggestion = SKILL_SUGGESTIONS.get(
                skill.lower(),
                DEFAULT_SUGGESTION.format(skill=skill.title()),
            )
            suggestions.append(suggestion)

        return suggestions
