from app.config import settings
from app.storage.minio_client import s3
from botocore.exceptions import ClientError


def ensure_bucket_exists():
    try:
        s3.head_bucket(Bucket=settings.MINIO_BUCKET)
    except ClientError:
        s3.create_bucket(Bucket=settings.MINIO_BUCKET)
