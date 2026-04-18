"""
S3 Service
Handles uploading resume and job description files to AWS S3.
Files are stored with a UUID prefix to avoid name collisions.
"""

import uuid
import logging
from fastapi import UploadFile, HTTPException
from botocore.exceptions import ClientError, NoCredentialsError
from app.core.aws_clients import get_s3_client
from app.core.config import settings

logger = logging.getLogger(__name__)


async def upload_file_to_s3(file: UploadFile, folder: str = "uploads") -> str:
    """
    Upload a file to S3 and return the S3 object key.

    Args:
        file: FastAPI UploadFile object
        folder: S3 "folder" prefix (e.g. "resumes", "job_descriptions")

    Returns:
        str: The S3 object key (path inside the bucket)
    """
    s3 = get_s3_client()

    # Generate a unique key to prevent overwriting existing files
    unique_id = uuid.uuid4().hex
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "pdf"
    s3_key = f"{folder}/{unique_id}_{file.filename}"

    try:
        # Read file bytes
        file_bytes = await file.read()

        # Upload to S3
        s3.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_bytes,
            ContentType=file.content_type or "application/pdf",
        )

        logger.info(f"Uploaded file to S3: s3://{settings.S3_BUCKET_NAME}/{s3_key}")
        return s3_key

    except NoCredentialsError:
        logger.error("AWS credentials not configured correctly.")
        raise HTTPException(
            status_code=500,
            detail="AWS credentials are not configured. Please check your .env file.",
        )
    except ClientError as e:
        logger.error(f"S3 upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")
    finally:
        # Reset file pointer for any subsequent reads
        await file.seek(0)


def get_s3_presigned_url(s3_key: str, expiry: int = 3600) -> str:
    """
    Generate a pre-signed URL to allow temporary public access to an S3 object.

    Args:
        s3_key: The S3 object key
        expiry: Expiry in seconds (default 1 hour)

    Returns:
        str: Pre-signed URL
    """
    s3 = get_s3_client()
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=expiry,
        )
        return url
    except ClientError as e:
        logger.error(f"Failed to generate pre-signed URL: {e}")
        raise HTTPException(status_code=500, detail="Could not generate file URL.")
