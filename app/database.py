import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import settings

conn = None


async def connect_db():
    global conn
    if conn is None:
        conn = psycopg2.connect(
            settings.DATABASE_URL,
            cursor_factory=RealDictCursor
        )
        print("✅ Connected to PostgreSQL")


async def disconnect_db():
    global conn
    if conn:
        conn.close()
        print("🔌 Disconnected from PostgreSQL")
