from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from app.database import conn
from app.auth.hashing import get_password_hash

router = APIRouter(prefix="/profile", tags=["Profile"])


class ProfileUpdate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


@router.get("/")
def get_profile(request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_superuser": user.is_superuser
    }


@router.put("/")
def update_profile(data: ProfileUpdate, request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    hashed_password = get_password_hash(data.password)

    with conn.cursor() as cur:
        cur.execute("""
            UPDATE users
            SET full_name = %s, email = %s, password = %s
            WHERE id = %s
        """, (data.full_name, data.email, hashed_password, user.id))
        conn.commit()

    return {"message": "Profile updated successfully"}


@router.delete("/")
def delete_profile(request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    with conn.cursor() as cur:
        cur.execute("DELETE FROM users WHERE id = %s", (user.id,))
        conn.commit()

    return {"message": "Account deleted"}