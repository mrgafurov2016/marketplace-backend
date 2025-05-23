from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List
from app.database import conn

router = APIRouter(prefix="/articles", tags=["Comments"])

class CommentCreate(BaseModel):
    content: str

class CommentOut(BaseModel):
    id: int
    article_id: int
    author_id: int
    content: str
    created_at: str


@router.post("/{article_id}/comments", response_model=CommentOut)
def add_comment(article_id: int, comment: CommentCreate, request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO comments (article_id, author_id, content)
            VALUES (%s, %s, %s)
            RETURNING id, article_id, author_id, content, created_at
            """,
            (article_id, user.id, comment.content),
        )
        new_comment = cur.fetchone()
        conn.commit()
        return new_comment


@router.get("/{article_id}/comments", response_model=List[CommentOut])
def get_comments(article_id: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, article_id, author_id, content, created_at
            FROM comments
            WHERE article_id = %s
            ORDER BY created_at DESC
            """,
            (article_id,),
        )
        return cur.fetchall()


@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    with conn.cursor() as cur:
        cur.execute("SELECT author_id FROM comments WHERE id = %s", (comment_id,))
        comment = cur.fetchone()

        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        if comment["author_id"] != user.id and not user.is_superuser:
            raise HTTPException(status_code=403, detail="Permission denied")

        cur.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        conn.commit()
        return {"message": "Comment deleted"}