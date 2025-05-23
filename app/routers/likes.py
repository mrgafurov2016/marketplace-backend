from fastapi import APIRouter, HTTPException, Request
from app.database import conn

router = APIRouter(prefix="/articles", tags=["Likes"])


@router.post("/{article_id}/like")
def like_article(article_id: int, request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO article_likes (article_id, user_id, is_like)
            VALUES (%s, %s, TRUE)
            ON CONFLICT (article_id, user_id)
            DO UPDATE SET is_like = TRUE, created_at = NOW()
        """, (article_id, user.id))
        conn.commit()
        return {"message": "Article liked"}


@router.post("/{article_id}/dislike")
def dislike_article(article_id: int, request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO article_likes (article_id, user_id, is_like)
            VALUES (%s, %s, FALSE)
            ON CONFLICT (article_id, user_id)
            DO UPDATE SET is_like = FALSE, created_at = NOW()
        """, (article_id, user.id))
        conn.commit()
        return {"message": "Article disliked"}


@router.get("/{article_id}/likes")
def get_article_likes(article_id: int):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE is_like = TRUE) AS likes,
                COUNT(*) FILTER (WHERE is_like = FALSE) AS dislikes
            FROM article_likes
            WHERE article_id = %s
        """, (article_id,))
        stats = cur.fetchone()
        return stats