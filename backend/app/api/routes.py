"""
API Routes
"""

import logging
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from app.services.orchestrator import run_full_analysis
from app.models.schemas import AnalysisResult
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=AnalysisResult, tags=["Analysis"])
async def analyze(
    resume: UploadFile = File(...),
    job_description_file: Optional[UploadFile] = File(None),
    job_description_text: Optional[str] = Form(None),
    use_aws: str = Form("false"),
):
    # Validate resume
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Resume must be a PDF file.")

    # Validate JD provided
    if not job_description_file and not job_description_text:
        raise HTTPException(status_code=400, detail="Please provide a job description PDF or text.")

    # Validate JD file type
    if job_description_file and not job_description_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Job description file must be a PDF.")

    # Convert string "true"/"false" to boolean
    use_aws_bool = use_aws.lower() == "true"

    try:
        result = await run_full_analysis(
            resume_file=resume,
            jd_file=job_description_file,
            jd_text=job_description_text,
            use_aws=use_aws_bool,
        )
        return result

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/decisions", tags=["Configuration"])
async def get_decision_thresholds():
    return {
        "thresholds": {
            "apply_now": {
                "min_score": settings.APPLY_THRESHOLD,
                "max_score": 100,
                "label": "APPLY NOW",
                "color": "green",
            },
            "improve_before_applying": {
                "min_score": settings.IMPROVE_THRESHOLD,
                "max_score": settings.APPLY_THRESHOLD - 1,
                "label": "IMPROVE BEFORE APPLYING",
                "color": "yellow",
            },
            "not_suitable": {
                "min_score": 0,
                "max_score": settings.IMPROVE_THRESHOLD - 1,
                "label": "NOT SUITABLE",
                "color": "red",
            },
        }
    }