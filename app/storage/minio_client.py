import boto3
from app.config import settings
from botocore.client import Config
from botocore.exceptions import ClientError

session = boto3.session.Session()

s3 = session.client(
    service_name='s3',
    endpoint_url=settings.minio_endpoint,
    aws_access_key_id=settings.minio_access_key,
    aws_secret_access_key=settings.minio_secret_key,
    config=Config(signature_version='s3v4'),
)


def ensure_bucket_exists():
    try:
        s3.head_bucket(Bucket=settings.minio_bucket)
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            s3.create_bucket(Bucket=settings.minio_bucket)
