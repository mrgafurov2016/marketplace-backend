from fastapi import APIRouter, HTTPException, Request
from app.database import conn

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.post("/{article_id}")
def add_bookmark(article_id: int, request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO article_bookmarks (article_id, user_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (article_id, user.id))
        conn.commit()
        return {"message": "Article bookmarked"}


@router.delete("/{article_id}")
def remove_bookmark(article_id: int, request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM article_bookmarks
            WHERE article_id = %s AND user_id = %s
        """, (article_id, user.id))
        conn.commit()
        return {"message": "Bookmark removed"}


@router.get("/")
def list_bookmarks(request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    with conn.cursor() as cur:
        cur.execute("""
            SELECT a.*
            FROM articles a
            JOIN article_bookmarks b ON a.id = b.article_id
            WHERE b.user_id = %s
            ORDER BY b.created_at DESC
        """, (user.id,))
        articles = cur.fetchall()
        return articles