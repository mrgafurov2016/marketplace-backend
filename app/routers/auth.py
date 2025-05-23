from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.database import conn
from app.auth import hash_password
from app.workers.email_tasks import send_email_task
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])


# Модель входящих данных при регистрации
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


# Модель ответа после регистрации
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime


@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate):
    hashed_password = hash_password(user.password)

    with conn.cursor() as cur:
        # Проверка: не зарегистрирован ли уже такой email
        cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует.")

        # Регистрация нового пользователя
        cur.execute(
            """
            INSERT INTO users (email, hashed_password, full_name)
            VALUES (%s, %s, %s)
            RETURNING id, email, full_name, is_active, is_superuser, created_at
            """,
            (user.email, hashed_password, user.full_name),
        )
        new_user = cur.fetchone()
        conn.commit()

    # Отправка письма через Celery
    send_email_task.delay(
        to_email=user.email,
        subject="Добро пожаловать!",
        body=f"Здравствуйте, {user.full_name or user.email}! Вы успешно зарегистрировались."
    )

    return UserOut(
        id=new_user[0],
        email=new_user[1],
        full_name=new_user[2],
        is_active=new_user[3],
        is_superuser=new_user[4],
        created_at=new_user[5],
    )