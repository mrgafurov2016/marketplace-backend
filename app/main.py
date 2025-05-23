from fastapi import FastAPI
from app.database import connect_db, disconnect_db
from app.routers import all_routers
from app.routers import articles
from app.routers import upload
from app.storage.utils import ensure_bucket_exists  # добавлено
from app.middleware.jwt_cookie_middleware import JWTAuthMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.routers import comments
from app.routers import likes
from app.routers import bookmarks
from app.routers import profile

app = FastAPI(title="Marketplace API")

# Подключаем все роутеры
app.include_router(articles.router)
app.include_router(upload.router)
app.add_middleware(JWTAuthMiddleware)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(bookmarks.router)
app.include_router(profile.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # настрой при необходимости
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in all_routers:
    app.include_router(router)

@app.on_event("startup")
async def startup():
    await connect_db()
    ensure_bucket_exists()  # добавлено

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

@app.get("/")
def read_root():
    return {"message": "Marketplace backend is running!"}

