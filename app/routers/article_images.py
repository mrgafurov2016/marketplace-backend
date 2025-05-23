from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
from app.database import conn
from app.storage.minio_client import s3
from app.config import settings
import uuid

router = APIRouter(prefix="/article-images", tags=["article images"])


class ArticleImageOut(BaseModel):
    id: int
    article_id: int
    image_url: str


@router.post("/", response_model=ArticleImageOut)
def upload_article_image(article_id: int = Form(...), file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]
    object_name = f"articles/{uuid.uuid4()}.{ext}"

    s3.upload_fileobj(file.file, settings.minio_bucket, object_name)

    image_url = f"{settings.minio_endpoint}/{settings.minio_bucket}/{object_name}"

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO article_images (article_id, image_url)
            VALUES (%s, %s)
            RETURNING id, article_id, image_url
            """,
            (article_id, image_url),
        )
        row = cur.fetchone()
        conn.commit()
        return row


@router.get("/by-article/{article_id}", response_model=List[ArticleImageOut])
def get_images_by_article(article_id: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, article_id, image_url
            FROM article_images
            WHERE article_id = %s
            ORDER BY id
            """,
            (article_id,),
        )
        return cur.fetchall()
