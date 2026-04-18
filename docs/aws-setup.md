# ☁️ AWS Setup Guide

Complete step-by-step guide to configure AWS S3 and AWS Comprehend for the Job Readiness Analyzer.

---

## Required AWS Services

| Service        | Purpose                          | Cost Model             |
|----------------|----------------------------------|------------------------|
| Amazon S3      | Store uploaded PDFs              | ~$0.023/GB/month       |
| AWS Comprehend | NLP key phrase extraction        | $0.0001 per 100 chars  |

For typical usage (10–50 analyses/day), cost is **under $1/month**.

---

## Step 1 — Create IAM Policy

Create a least-privilege policy instead of using full-access managed policies.

Go to **IAM → Policies → Create Policy** and paste this JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::job-readiness-uploads",
        "arn:aws:s3:::job-readiness-uploads/*"
      ]
    },
    {
      "Sid": "ComprehendAccess",
      "Effect": "Allow",
      "Action": [
        "comprehend:DetectKeyPhrases",
        "comprehend:DetectEntities",
        "comprehend:DetectDominantLanguage"
      ],
      "Resource": "*"
    }
  ]
}
```

Name it: `JobReadinessAnalyzerPolicy`

---

## Step 2 — Create IAM User

1. Go to **IAM → Users → Create User**
2. Username: `job-readiness-app`
3. Select: **Attach policies directly**
4. Attach: `JobReadinessAnalyzerPolicy`
5. Click: **Create user**
6. Go to the user → **Security credentials** tab
7. Click **Create access key** → Application running outside AWS
8. Copy the **Access Key ID** and **Secret Access Key** — you won't see these again!

---

## Step 3 — Create S3 Bucket

### Via AWS CLI:
```bash
# Install AWS CLI first: https://aws.amazon.com/cli/
aws configure  # Enter your access key, secret, region

# Create bucket
aws s3 mb s3://job-readiness-uploads --region us-east-1

# Verify
aws s3 ls
```

### Via AWS Console:
1. Go to **S3 → Create bucket**
2. Bucket name: `job-readiness-uploads` (must be globally unique — add your initials if taken)
3. Region: `us-east-1` (or your preferred region)
4. **Block all public access**: ✅ Keep enabled (files are accessed via pre-signed URLs)
5. Click **Create bucket**

---

## Step 4 — Configure Environment

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your values:

```env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
S3_BUCKET_NAME=job-readiness-uploads
```

---

## Step 5 — Test the Connection

```bash
cd backend
source venv/bin/activate
python -c "
import boto3
from app.core.config import settings

# Test S3
s3 = boto3.client('s3',
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)
s3.put_object(Bucket=settings.S3_BUCKET_NAME, Key='test.txt', Body=b'hello')
print('✅ S3 connection: OK')

# Test Comprehend
comp = boto3.client('comprehend',
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)
result = comp.detect_key_phrases(Text='Python developer with AWS experience', LanguageCode='en')
print('✅ Comprehend connection: OK')
print('Phrases:', [p['Text'] for p in result['KeyPhrases']])
"
```

---

## AWS Comprehend Limits

| Limit                    | Value           |
|--------------------------|-----------------|
| Max text per request     | 5,000 bytes     |
| Max requests per second  | 20 (default)    |
| Supported languages      | 100+            |

The `comprehend_service.py` automatically **chunks large texts** to stay within the 5,000 byte limit.

---

## Estimated Costs

For a student project or small team:

| Usage              | S3 Cost    | Comprehend Cost | Total/Month |
|--------------------|------------|-----------------|-------------|
| 10 analyses/day    | ~$0.01     | ~$0.30          | ~$0.31      |
| 100 analyses/day   | ~$0.05     | ~$3.00          | ~$3.05      |
| 1000 analyses/day  | ~$0.50     | ~$30.00         | ~$30.50     |

*AWS Free Tier includes 50,000 Comprehend API units/month for the first 12 months.*
