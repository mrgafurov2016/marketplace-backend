from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.database import conn
from app.auth import hash_password, verify_password
from jose import jwt
from datetime import datetime, timedelta
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(user: UserCreate):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_pwd = hash_password(user.password)
        cur.execute(
            """
            INSERT INTO users (email, hashed_password, full_name)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (user.email, hashed_pwd, user.full_name),
        )
        user_id = cur.fetchone()["id"]
        conn.commit()
        return {"message": "User registered", "user_id": user_id}


@router.post("/login")
def login(user: UserLogin):
    with conn.cursor() as cur:
        cur.execute("SELECT id, hashed_password FROM users WHERE email = %s", (user.email,))
        db_user = cur.fetchone()
        if not db_user or not verify_password(user.password, db_user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token_data = {
            "sub": str(db_user["id"]),
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        return {"access_token": token, "token_type": "bearer"}
