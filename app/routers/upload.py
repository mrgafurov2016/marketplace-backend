from fastapi import APIRouter, UploadFile, File, HTTPException
from uuid import uuid4
from app.storage.minio_client import s3
from app.config import settings
from botocore.exceptions import BotoCoreError, ClientError

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]
    key = f"articles/{uuid4()}.{ext}"

    try:
        s3.upload_fileobj(
            file.file,
            Bucket=settings.minio_bucket,
            Key=key,
            ExtraArgs={"ContentType": file.content_type}
        )
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=500, detail="Upload failed") from e

    image_url = f"{settings.minio_endpoint}/{settings.minio_bucket}/{key}"
    return {"image_url": image_url}
