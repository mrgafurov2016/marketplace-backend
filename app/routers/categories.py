from fastapi import APIRouter, HTTPException
from app.database import conn

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/")
def create_category(name: str, description: str = ""):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO categories (name, description) VALUES (%s, %s) RETURNING id", (name, description))
        category_id = cur.fetchone()["id"]
        conn.commit()
        return {"id": category_id, "name": name, "description": description}


@router.get("/")
def list_categories():
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM categories")
        categories = cur.fetchall()
        return categories


@router.get("/{category_id}")
def get_category(category_id: int):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
        category = cur.fetchone()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
