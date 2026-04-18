"""
Analysis Orchestrator
"""

import logging
from typing import Optional
from fastapi import UploadFile

from app.services.s3_service import upload_file_to_s3
from app.services.pdf_service import extract_text_from_pdf_upload, clean_text
from app.services.comprehend_service import extract_key_phrases
from app.services.mongo_service import save_analysis
from app.services.skill_intelligence import (
    identify_skills,
    categorize_skills,
    fallback_skill_extraction,
)
from app.services.analysis_engines import (
    ComparisonEngine,
    ScoringEngine,
    DecisionEngine,
    SuggestionEngine,
)
from app.models.schemas import AnalysisResult

logger = logging.getLogger(__name__)


async def run_full_analysis(
    resume_file: UploadFile,
    jd_file: Optional[UploadFile] = None,
    jd_text: Optional[str] = None,
    use_aws: bool = False,
) -> AnalysisResult:

    # Fix: handle string "false"/"true" passed from form data
    if isinstance(use_aws, str):
        use_aws = use_aws.lower() == "true"

    # ── Stage 1: S3 Upload (only if AWS enabled) ──────────────────────────────
    s3_resume_key = None
    s3_jd_key = None

    if use_aws:
        try:
            logger.info("Uploading resume to S3...")
            s3_resume_key = await upload_file_to_s3(resume_file, folder="resumes")
            if jd_file:
                logger.info("Uploading JD to S3...")
                s3_jd_key = await upload_file_to_s3(jd_file, folder="job_descriptions")
        except Exception as e:
            logger.warning(f"S3 upload skipped: {e}")

    # ── Stage 2: Extract text from PDFs ───────────────────────────────────────
    logger.info("Extracting text from resume PDF...")
    resume_text = await extract_text_from_pdf_upload(resume_file)
    resume_text = clean_text(resume_text)

    if jd_file:
        logger.info("Extracting text from JD PDF...")
        jd_text = await extract_text_from_pdf_upload(jd_file)
        jd_text = clean_text(jd_text)
        jd_source = jd_file.filename
    else:
        jd_source = "text input"
        jd_text = clean_text(jd_text or "")

    if not jd_text:
        raise ValueError("No job description text provided.")

    # ── Stage 3: Skill Extraction ─────────────────────────────────────────────
    if use_aws:
        try:
            logger.info("Running AWS Comprehend...")
            resume_phrases = extract_key_phrases(resume_text)
            jd_phrases = extract_key_phrases(jd_text)
            resume_skills = identify_skills(resume_phrases)
            job_skills = identify_skills(jd_phrases)
        except Exception as e:
            logger.warning(f"Comprehend failed, using fallback: {e}")
            resume_skills = fallback_skill_extraction(resume_text)
            job_skills = fallback_skill_extraction(jd_text)
    else:
        logger.info("Using local keyword extraction...")
        resume_skills = fallback_skill_extraction(resume_text)
        job_skills = fallback_skill_extraction(jd_text)
    

    logger.info(f"Resume skills: {resume_skills}")
    logger.info(f"Job skills:    {job_skills}")

    # ── Stage 4: Categorize ───────────────────────────────────────────────────
    resume_categories = categorize_skills(resume_skills)
    job_categories = categorize_skills(job_skills)

    # ── Stage 5: Compare ──────────────────────────────────────────────────────
    matched_skills, missing_skills = ComparisonEngine.compare(resume_skills, job_skills)

    # ── Stage 6: Score ────────────────────────────────────────────────────────
    score = ScoringEngine.calculate_overall_score(matched_skills, missing_skills)
    match_breakdown = ScoringEngine.calculate_category_breakdown(resume_categories, job_categories)

    # ── Stage 7: Decide ───────────────────────────────────────────────────────
    decision = DecisionEngine.decide(score)

    # ── Stage 8: Suggestions ──────────────────────────────────────────────────
    suggestions = SuggestionEngine.generate_suggestions(missing_skills)

    logger.info(f"Decision: {decision} | Score: {score}%")
    

    return AnalysisResult(
        decision=decision,
        confidence=score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        resume_skills=sorted(resume_skills),
        job_skills=sorted(job_skills),
        resume_skill_categories=resume_categories,
        job_skill_categories=job_categories,
        match_breakdown=match_breakdown,
        suggestions=suggestions,
        resume_filename=resume_file.filename,
        job_description_source=jd_source,
        s3_resume_key=s3_resume_key,
        s3_jd_key=s3_jd_key,
    )