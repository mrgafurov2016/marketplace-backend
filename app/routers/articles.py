from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from typing import List, Optional
from app.database import conn
from app.workers.email_tasks import send_email_task

router = APIRouter(prefix="/articles", tags=["articles"])


class ArticleCreate(BaseModel):
    title: str
    content: str
    author_id: int
    category_id: Optional[int] = None
    image_url: Optional[str] = None


class ArticleOut(ArticleCreate):
    id: int


@router.post("/", response_model=ArticleOut)
def create_article(article: ArticleCreate):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO articles (title, content, author_id, category_id, image_url)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                article.title,
                article.content,
                article.author_id,
                article.category_id,
                article.image_url,
            ),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create article")
        conn.commit()

        send_email_task.delay(
            to_email="user@example.com",
            subject="Новая статья опубликована",
            body=f"Статья '{article.title}' была опубликована."
        )

        return {**article.dict(), "id": row["id"]}


@router.get("/", response_model=List[ArticleOut])
def list_articles(
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    page_number: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
):
    offset = (page_number - 1) * page_size
    base_query = "SELECT * FROM articles WHERE TRUE"
    params = []

    if search:
        base_query += " AND tsv @@ plainto_tsquery(%s)"
        params.append(search)

    if category_id:
        base_query += " AND category_id = %s"
        params.append(category_id)

    base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([page_size, offset])

    with conn.cursor() as cur:
        cur.execute(base_query, tuple(params))
        articles = cur.fetchall()
        return articles


@router.get("/{article_id}", response_model=ArticleOut)
def get_article(article_id: int):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
        article = cur.fetchone()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article


@router.put("/{article_id}", response_model=ArticleOut)
def update_article(article_id: int, updated: ArticleCreate, request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    with conn.cursor() as cur:
        cur.execute("SELECT author_id FROM articles WHERE id = %s", (article_id,))
        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Article not found")

        is_author = result["author_id"] == user["id"]
        if not is_author and not user["is_superuser"]:
            raise HTTPException(status_code=403, detail="Permission denied")

        cur.execute(
            """
            UPDATE articles
            SET title = %s, content = %s, author_id = %s, category_id = %s, image_url = %s
            WHERE id = %s
            RETURNING *
            """,
            (
                updated.title,
                updated.content,
                updated.author_id,
                updated.category_id,
                updated.image_url,
                article_id,
            ),
        )
        article = cur.fetchone()
        conn.commit()
        return article


@router.delete("/{article_id}")
def delete_article(article_id: int, request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
        article = cur.fetchone()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        is_author = article["author_id"] == user["id"]
        if not is_author and not user["is_superuser"]:
            raise HTTPException(status_code=403, detail="Permission denied")

        cur.execute(
            """
            INSERT INTO deleted_articles (
                original_id, title, content, author_id, category_id, image_url, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                article["id"],
                article["title"],
                article["content"],
                article["author_id"],
                article["category_id"],
                article["image_url"],
                article["created_at"],
            ),
        )

        cur.execute("DELETE FROM articles WHERE id = %s", (article_id,))
        conn.commit()
        return {"message": "Article moved to deleted_articles"}