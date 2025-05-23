from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database import conn

router = APIRouter(prefix="/users", tags=["Users"])


class UserUpdate(BaseModel):
    username: str
    email: EmailStr


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me")
def update_me(data: UserUpdate, current_user: User = Depends(get_current_user)):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET username = %s, email = %s WHERE id = %s RETURNING id, username, email",
            (data.username, data.email, current_user.id),
        )
        updated = cur.fetchone()
        if not updated:
            raise HTTPException(status_code=404, detail="User not found")
        conn.commit()
        return updated


@router.delete("/me")
def delete_me(current_user: User = Depends(get_current_user)):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM users WHERE id = %s", (current_user.id,))
        conn.commit()
    return {"message": "User account deleted"}