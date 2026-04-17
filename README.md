# ⚡ AI Job Readiness Analyzer

> Upload your resume. Paste a job description. Get a clear decision: **Apply Now**, **Improve First**, or **Not Suitable** — backed by AWS Comprehend NLP and a curated skill taxonomy of 200+ technologies.

---

## 📸 What It Does

```
Resume PDF + Job Description → NLP → Skill Gap → Decision + Roadmap
```

**Pipeline:**
1. Extracts text from PDFs using `pdfplumber`
2. Sends text to **AWS Comprehend** `detect_key_phrases`
3. Filters phrases through a **200+ skill taxonomy** (languages, frameworks, tools, cloud, databases, concepts)
4. **Compares** resume skills vs job requirements
5. **Scores** the match (0–100%)
6. **Decides**: `APPLY NOW` / `IMPROVE BEFORE APPLYING` / `NOT SUITABLE`
7. Generates a **personalized learning roadmap** for missing skills

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React + Vite)                  │
│   UploadForm → LoadingState → DecisionBanner → SkillMatrix       │
│                           → MatchChart → SuggestionRoadmap       │
└──────────────────────────┬──────────────────────────────────────┘
                           │ POST /api/v1/analyze (multipart)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│                                                                   │
│  routes.py → orchestrator.py                                      │
│                    │                                              │
│       ┌────────────┼────────────────────┐                        │
│       ▼            ▼                    ▼                        │
│  s3_service   pdf_service       comprehend_service               │
│       │            │                    │                        │
│       ▼            ▼                    ▼                        │
│    AWS S3    pdfplumber text    AWS Comprehend NLP               │
│                                         │                        │
│                              skill_intelligence.py               │
│                              (200+ skill taxonomy)               │
│                                         │                        │
│                              analysis_engines.py                 │
│                         ┌───────────────┤                        │
│                         ▼               ▼                        │
│                  ComparisonEngine   ScoringEngine                │
│                         │               │                        │
│                         ▼               ▼                        │
│                  DecisionEngine   SuggestionEngine               │
│                                                                   │
│                      → AnalysisResult JSON                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
ai-job-readiness/
│
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example                   # Copy to .env
│   └── app/
│       ├── api/
│       │   └── routes.py              # HTTP endpoints
│       ├── core/
│       │   ├── config.py              # Pydantic settings
│       │   └── aws_clients.py         # Boto3 client factory
│       ├── models/
│       │   └── schemas.py             # Pydantic response models
│       └── services/
│           ├── orchestrator.py        # ← Pipeline coordinator
│           ├── s3_service.py          # AWS S3 upload/presign
│           ├── pdf_service.py         # pdfplumber text extraction
│           ├── comprehend_service.py  # AWS Comprehend NLP
│           ├── skill_intelligence.py  # 200+ skill taxonomy + categorizer
│           └── analysis_engines.py   # Comparison/Scoring/Decision/Suggestion
│
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── main.jsx
│       ├── App.jsx                    # Root — state machine
│       ├── App.module.css
│       ├── styles/
│       │   └── global.css             # Design system variables
│       ├── hooks/
│       │   └── useAnalysis.js         # Analysis lifecycle hook
│       ├── services/
│       │   └── api.js                 # Axios API client
│       ├── utils/
│       │   └── helpers.js             # Color utils, labels
│       └── components/
│           ├── UploadForm.jsx         # Drag-drop resume + JD upload
│           ├── LoadingState.jsx       # Animated processing steps
│           ├── DecisionBanner.jsx     # Hero verdict with animated score ring
│           ├── SkillMatrix.jsx        # Matched/missing chips + category bars
│           ├── MatchChart.jsx         # Recharts radar/bar visualization
│           ├── SuggestionRoadmap.jsx  # Numbered learning roadmap
│           └── ResultsPage.jsx        # Full results dashboard
│
└── docs/
    ├── aws-setup.md
    └── api-reference.md
```

---

## 🚀 Quick Start (Local — No AWS Required)

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env (no AWS keys needed for local mode)
cp .env.example .env

# Start the server
uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000  
Swagger docs at: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at: http://localhost:3000

### 3. Use Local Mode (No AWS)

On the upload form, **leave the "Use AWS" checkbox unchecked**.  
The system will use fast local keyword matching — no credentials needed.

---

## ☁️ AWS Setup (Full Production Mode)

### Step 1 — Create IAM User

1. Open [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Create a new user: `job-readiness-app`
3. Attach these managed policies:
   - `AmazonS3FullAccess` (or a custom policy scoped to your bucket)
   - `ComprehendReadOnly`
4. Create **Access Keys** and copy them

### Step 2 — Create S3 Bucket

```bash
aws s3 mb s3://job-readiness-uploads --region us-east-1
```

Or create via the AWS Console. The bucket name must match `S3_BUCKET_NAME` in your `.env`.

### Step 3 — Configure .env

```bash
cd backend
cp .env.example .env
```

Edit `.env`:

```env
AWS_ACCESS_KEY_ID=AKIA...your-key...
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=job-readiness-uploads
```

### Step 4 — Enable AWS on the Frontend

Check the **"Use AWS"** checkbox in the upload form before submitting.

---

## 🎯 Decision Engine Thresholds

| Score     | Decision                    | Meaning                              |
|-----------|----------------------------|--------------------------------------|
| ≥ 80%     | 🚀 APPLY NOW               | Strong skill match                   |
| 50–79%    | 📈 IMPROVE BEFORE APPLYING | Partial match — close the gaps first |
| < 50%     | 🛑 NOT SUITABLE            | Significant gaps — build skills first|

Thresholds are configurable in `.env`:

```env
APPLY_THRESHOLD=80
IMPROVE_THRESHOLD=50
```

---

## 📡 API Reference

### `POST /api/v1/analyze`

**Content-Type:** `multipart/form-data`

| Field                   | Type   | Required | Description                         |
|-------------------------|--------|----------|-------------------------------------|
| `resume`                | File   | ✅        | Resume PDF                          |
| `job_description_file`  | File   | ⭕        | Job description PDF                 |
| `job_description_text`  | string | ⭕        | Job description as plain text       |
| `use_aws`               | bool   | ⭕        | Default: `true`                     |

*Either `job_description_file` or `job_description_text` must be provided.*

**Response:**

```json
{
  "decision": "IMPROVE BEFORE APPLYING",
  "confidence": 65,
  "matched_skills": ["python", "aws", "docker"],
  "missing_skills": ["kubernetes", "fastapi", "terraform"],
  "resume_skills": ["python", "aws", "docker", "react", "git"],
  "job_skills": ["python", "aws", "docker", "kubernetes", "fastapi", "terraform"],
  "resume_skill_categories": {
    "languages": ["python"],
    "frameworks": ["react"],
    "tools": ["docker", "git"],
    "cloud": ["aws"],
    "databases": [],
    "concepts": []
  },
  "job_skill_categories": {
    "languages": ["python"],
    "frameworks": ["fastapi"],
    "tools": ["docker", "kubernetes", "terraform"],
    "cloud": ["aws"],
    "databases": [],
    "concepts": []
  },
  "match_breakdown": {
    "languages": 100.0,
    "frameworks": 0.0,
    "tools": 33.3,
    "cloud": 100.0,
    "databases": 100.0,
    "concepts": 100.0
  },
  "suggestions": [
    "Take 'Kubernetes for Absolute Beginners' on Udemy and deploy an app on Minikube.",
    "Build a REST API using FastAPI — official docs at fastapi.tiangolo.com are excellent.",
    "Follow HashiCorp's official Terraform getting-started guide on AWS."
  ],
  "resume_filename": "john_doe_resume.pdf",
  "job_description_source": "text input"
}
```

### `GET /api/v1/decisions`

Returns the configured decision thresholds.

---

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## 🔧 Tech Stack

| Layer      | Technology              |
|------------|------------------------|
| Frontend   | React 18, Vite, Recharts, CSS Modules |
| Backend    | FastAPI, Pydantic v2   |
| PDF        | pdfplumber             |
| NLP        | AWS Comprehend         |
| Storage    | AWS S3 + Boto3         |
| Database   | MongoDB (optional)     |
| Fonts      | Syne, DM Mono, Inter   |

---

## 🛣️ Roadmap / Bonus Ideas

- [ ] MongoDB persistence — save analysis history per user
- [ ] Export results as PDF report
- [ ] Side-by-side multi-job comparison
- [ ] LinkedIn profile URL input (instead of PDF)
- [ ] Skill trending — highlight skills in high demand right now
- [ ] Auth layer (Clerk / Auth0) for user accounts
