import boto3, os
from dotenv import load_dotenv
load_dotenv()

print("Testing AWS connection...")
print(f"Region: {os.getenv('AWS_REGION')}")
print(f"Bucket: {os.getenv('S3_BUCKET_NAME')}")
print(f"Key starts with: {os.getenv('AWS_ACCESS_KEY_ID', 'NOT SET')[:8]}...")

# Test S3
try:
    s3 = boto3.client("s3",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    s3.put_object(
        Bucket=os.getenv("S3_BUCKET_NAME"),
        Key="test/hello.txt",
        Body=b"Hello from Job Readiness App!"
    )
    print("✅ S3 working!")
except Exception as e:
    print(f"❌ S3 failed: {e}")

# Test Comprehend
try:
    comprehend = boto3.client("comprehend",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    result = comprehend.detect_key_phrases(
        Text="Looking for a Python developer with FastAPI and AWS experience.",
        LanguageCode="en"
    )
    phrases = [p["Text"] for p in result["KeyPhrases"]]
    print(f"✅ Comprehend working!")
    print(f"   Phrases found: {phrases}")
except Exception as e:
    print(f"❌ Comprehend failed: {e}")