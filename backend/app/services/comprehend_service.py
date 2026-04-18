"""
AWS Comprehend Service
Uses AWS Comprehend's detect_key_phrases API to extract meaningful phrases
from resume and job description text.

AWS Comprehend has a 5,000 byte limit per API call, so we chunk large texts.
"""

import logging
from typing import List
from botocore.exceptions import ClientError
from app.core.aws_clients import get_comprehend_client

logger = logging.getLogger(__name__)

# AWS Comprehend limit: 5000 UTF-8 bytes per request
COMPREHEND_BYTE_LIMIT = 4800  # Use 4800 to be safe


def chunk_text(text: str, byte_limit: int = COMPREHEND_BYTE_LIMIT) -> List[str]:
    """
    Split text into chunks that fit within AWS Comprehend's byte limit.

    Args:
        text: Input text
        byte_limit: Max bytes per chunk

    Returns:
        List of text chunks
    """
    chunks = []
    current_chunk = []
    current_size = 0

    for line in text.splitlines():
        line_bytes = len(line.encode("utf-8"))
        if current_size + line_bytes > byte_limit:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_size = line_bytes
        else:
            current_chunk.append(line)
            current_size += line_bytes

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks if chunks else [text[:byte_limit]]


def extract_key_phrases(text: str) -> List[str]:
    """
    Extract key phrases from text using AWS Comprehend.
    Handles chunking for large texts automatically.

    Args:
        text: Input text (resume or job description)

    Returns:
        List of extracted key phrases (strings)
    """
    comprehend = get_comprehend_client()
    all_phrases = []

    chunks = chunk_text(text)
    logger.info(f"Sending {len(chunks)} chunk(s) to AWS Comprehend.")

    for i, chunk in enumerate(chunks):
        try:
            response = comprehend.detect_key_phrases(
                Text=chunk,
                LanguageCode="en",
            )
            phrases = [
                item["Text"].lower().strip()
                for item in response.get("KeyPhrases", [])
                if item.get("Score", 0) >= 0.85  # Only use high-confidence phrases
            ]
            all_phrases.extend(phrases)
            logger.info(f"Chunk {i+1}: extracted {len(phrases)} phrases.")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            logger.error(f"Comprehend API error on chunk {i+1}: {error_code} — {e}")
            # Continue processing other chunks even if one fails
            continue

    return list(set(all_phrases))  # De-duplicate
