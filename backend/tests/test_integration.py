"""
Integration Tests — FastAPI Endpoint
Tests the full /analyze endpoint using httpx TestClient.
Run with: pytest tests/ -v
"""

import io
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def make_minimal_pdf(text: str = "Python developer with AWS experience") -> bytes:
    """
    Creates a minimal valid single-page PDF in pure bytes.
    Used for testing without needing real PDF files.
    """
    content = text.encode("latin-1", errors="replace")
    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]\n"
        b"   /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font\n"
        b"   /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length " + str(len(content) + 50).encode() + b" >>\nstream\n"
        b"BT /F1 12 Tf 50 750 Td (" + content + b") Tj ET\nendstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n9\n%%EOF"
    )
    return pdf


class TestHealthEndpoints:

    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_decisions_endpoint(self):
        response = client.get("/api/v1/decisions")
        assert response.status_code == 200
        data = response.json()
        assert "thresholds" in data
        assert "apply_now" in data["thresholds"]


class TestAnalyzeEndpoint:

    def test_missing_resume_returns_422(self):
        response = client.post(
            "/api/v1/analyze",
            data={"job_description_text": "Python developer needed", "use_aws": "false"},
        )
        assert response.status_code == 422

    def test_missing_jd_returns_400(self):
        pdf_bytes = make_minimal_pdf("Python AWS developer")
        response = client.post(
            "/api/v1/analyze",
            files={"resume": ("resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
            data={"use_aws": "false"},
        )
        assert response.status_code == 400
        assert "job description" in response.json()["detail"].lower()

    def test_non_pdf_resume_returns_400(self):
        response = client.post(
            "/api/v1/analyze",
            files={"resume": ("resume.docx", io.BytesIO(b"fake docx"), "application/vnd.openxmlformats")},
            data={"job_description_text": "Python developer needed", "use_aws": "false"},
        )
        assert response.status_code == 400

    def test_full_analysis_local_mode(self):
        """
        Full pipeline test using local (no AWS) mode.
        Uses synthetic PDFs containing known skill keywords.
        """
        resume_text = (
            "Experienced Python developer with 3 years of experience. "
            "Skilled in React, Docker, Git, PostgreSQL, and AWS. "
            "Built REST APIs and deployed microservices."
        )
        jd_text = (
            "We are looking for a Python backend developer. "
            "Required: Python, FastAPI, Docker, Kubernetes, PostgreSQL, AWS. "
            "Nice to have: React, CI/CD experience."
        )

        resume_pdf = make_minimal_pdf(resume_text)

        response = client.post(
            "/api/v1/analyze",
            files={"resume": ("test_resume.pdf", io.BytesIO(resume_pdf), "application/pdf")},
            data={
                "job_description_text": jd_text,
                "use_aws": "false",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Structure checks
        assert "decision" in data
        assert "confidence" in data
        assert "matched_skills" in data
        assert "missing_skills" in data
        assert "suggestions" in data
        assert "match_breakdown" in data

        # Decision must be one of the valid values
        assert data["decision"] in ["APPLY NOW", "IMPROVE BEFORE APPLYING", "NOT SUITABLE"]

        # Score must be 0–100
        assert 0 <= data["confidence"] <= 100

        # Python and Docker should be matched (present in both)
        assert "python" in data["matched_skills"] or "docker" in data["matched_skills"]

        # Suggestions count should equal missing skills count
        assert len(data["suggestions"]) == len(data["missing_skills"])

        print(f"\n✅ Decision: {data['decision']} ({data['confidence']}%)")
        print(f"   Matched:  {data['matched_skills']}")
        print(f"   Missing:  {data['missing_skills']}")
