"""
AWS client factory.
Centralizes Boto3 client creation so credentials are configured in one place.
"""

import boto3
from app.core.config import settings


def get_s3_client():
    """Returns a configured Boto3 S3 client."""
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def get_comprehend_client():
    """Returns a configured Boto3 Comprehend client."""
    return boto3.client(
        "comprehend",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
