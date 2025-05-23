from fastapi import APIRouter, Depends, HTTPException
from app.database import conn
from app.auth.dependencies import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/favorites", tags=["Favorites"])

@router.post("/{article_id}")
def add_to_favorites(article_id: int, current_user: User = Depends(get_current_user)):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM articles WHERE id = %s", (article_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Article not found")

        try:
            cur.execute("""
                INSERT INTO favorites (user_id, article_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (current_user.id, article_id))
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Added to favorites"}

@router.get("/")
def get_favorites(current_user: User = Depends(get_current_user)):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT a.*
            FROM articles a
            JOIN favorites f ON a.id = f.article_id
            WHERE f.user_id = %s
            ORDER BY f.created_at DESC
        """, (current_user.id,))
        return cur.fetchall()

@router.delete("/{article_id}")
def remove_from_favorites(article_id: int, current_user: User = Depends(get_current_user)):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM favorites
            WHERE user_id = %s AND article_id = %s
        """, (current_user.id, article_id))
        conn.commit()

    return {"message": "Removed from favorites"}