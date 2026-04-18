"""
Unit Tests for Analysis Engines
Run with: pytest tests/ -v
"""

import pytest
from app.services.analysis_engines import (
    ComparisonEngine,
    ScoringEngine,
    DecisionEngine,
    SuggestionEngine,
)
from app.services.skill_intelligence import (
    identify_skills,
    categorize_skills,
    fallback_skill_extraction,
)
from app.models.schemas import SkillCategories


# ── ComparisonEngine Tests ─────────────────────────────────────────────────────

class TestComparisonEngine:

    def test_matched_and_missing(self):
        resume  = {"python", "aws", "docker"}
        job     = {"python", "aws", "kubernetes", "fastapi"}
        matched, missing = ComparisonEngine.compare(resume, job)

        assert set(matched) == {"python", "aws"}
        assert set(missing) == {"kubernetes", "fastapi"}

    def test_perfect_match(self):
        skills = {"python", "react", "git"}
        matched, missing = ComparisonEngine.compare(skills, skills.copy())
        assert len(matched) == 3
        assert len(missing) == 0

    def test_zero_match(self):
        resume = {"java", "spring"}
        job    = {"python", "fastapi"}
        matched, missing = ComparisonEngine.compare(resume, job)
        assert len(matched) == 0
        assert len(missing) == 2

    def test_empty_inputs(self):
        matched, missing = ComparisonEngine.compare(set(), set())
        assert matched == []
        assert missing == []


# ── ScoringEngine Tests ────────────────────────────────────────────────────────

class TestScoringEngine:

    def test_perfect_score(self):
        score = ScoringEngine.calculate_overall_score(["python", "aws"], [])
        assert score == 100

    def test_zero_score(self):
        score = ScoringEngine.calculate_overall_score([], ["python", "aws"])
        assert score == 0

    def test_partial_score(self):
        score = ScoringEngine.calculate_overall_score(["python"], ["aws", "kubernetes"])
        # 1 matched / (1+2) total = 33%
        assert score == 33

    def test_empty_inputs(self):
        score = ScoringEngine.calculate_overall_score([], [])
        assert score == 0


# ── DecisionEngine Tests ──────────────────────────────────────────────────────

class TestDecisionEngine:

    def test_apply_now_at_threshold(self):
        assert DecisionEngine.decide(80) == "APPLY NOW"

    def test_apply_now_above_threshold(self):
        assert DecisionEngine.decide(100) == "APPLY NOW"
        assert DecisionEngine.decide(95) == "APPLY NOW"

    def test_improve_at_threshold(self):
        assert DecisionEngine.decide(50) == "IMPROVE BEFORE APPLYING"

    def test_improve_just_below_apply(self):
        assert DecisionEngine.decide(79) == "IMPROVE BEFORE APPLYING"

    def test_not_suitable_at_49(self):
        assert DecisionEngine.decide(49) == "NOT SUITABLE"

    def test_not_suitable_at_zero(self):
        assert DecisionEngine.decide(0) == "NOT SUITABLE"


# ── SuggestionEngine Tests ────────────────────────────────────────────────────

class TestSuggestionEngine:

    def test_known_skill_suggestions(self):
        suggestions = SuggestionEngine.generate_suggestions(["docker", "fastapi"])
        assert len(suggestions) == 2
        assert "Docker" in suggestions[0] or "docker" in suggestions[0].lower()
        assert "FastAPI" in suggestions[1] or "fastapi" in suggestions[1].lower()

    def test_unknown_skill_gets_default(self):
        suggestions = SuggestionEngine.generate_suggestions(["obscureskill123"])
        assert len(suggestions) == 1
        assert "obscureskill123" in suggestions[0].lower() or "Obscureskill123" in suggestions[0]

    def test_empty_missing_skills(self):
        suggestions = SuggestionEngine.generate_suggestions([])
        assert suggestions == []


# ── Skill Intelligence Tests ──────────────────────────────────────────────────

class TestSkillIntelligence:

    def test_identify_from_phrases(self):
        phrases = ["python developer", "experience with aws", "docker containerization"]
        skills = identify_skills(phrases)
        assert "python" in skills
        assert "aws" in skills
        assert "docker" in skills

    def test_alias_matching(self):
        phrases = ["k8s experience", "js developer", "golang backend"]
        skills = identify_skills(phrases)
        assert "kubernetes" in skills
        assert "javascript" in skills
        assert "go" in skills

    def test_fallback_extraction(self):
        text = "Looking for a Python developer with experience in React, Docker and AWS."
        skills = fallback_skill_extraction(text)
        assert "python" in skills
        assert "react" in skills
        assert "docker" in skills
        assert "aws" in skills

    def test_categorize_skills(self):
        skills = {"python", "react", "docker", "aws", "postgresql", "machine learning"}
        cats = categorize_skills(skills)
        assert "python" in cats.languages
        assert "react" in cats.frameworks
        assert "docker" in cats.tools
        assert "aws" in cats.cloud
        assert "postgresql" in cats.databases
        assert "machine learning" in cats.concepts
