from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import HTTPException
from jose import jwt, JWTError
from app.auth.models import User
from app.database import conn
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")  # замените на .env
ALGORITHM = "HS256"


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get("access_token")

        if token:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("sub")

                if user_id is None:
                    raise HTTPException(status_code=401, detail="Invalid JWT payload")

                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                    user = cur.fetchone()

                if user:
                    request.state.user = User(**user)
                else:
                    request.state.user = None
            except JWTError:
                request.state.user = None
        else:
            request.state.user = None

        response = await call_next(request)
        return response