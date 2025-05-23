from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import conn

router = APIRouter(prefix="/products", tags=["Products"])

class ProductIn(BaseModel):
    title: str
    description: str | None = None
    price: float
    image_url: str | None = None

@router.post("/")
async def create_product(product: ProductIn):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO products (title, description, price, image_url)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (product.title, product.description, product.price, product.image_url))
        product_id = cur.fetchone()["id"]
        conn.commit()
        return {"id": product_id}

@router.get("/")
async def get_products():
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        return products
