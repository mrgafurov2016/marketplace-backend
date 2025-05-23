-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица категорий
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица статей
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица изображений статей (для поддержки нескольких изображений на одну статью)
CREATE TABLE IF NOT EXISTS article_images (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Таблица товаров
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL
);


-- Таблица удалённых статей
CREATE TABLE IF NOT EXISTS deleted_articles (
    id SERIAL PRIMARY KEY,
    original_id INTEGER,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER,
    category_id INTEGER,
    image_url TEXT,
    created_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE articles ADD COLUMN IF NOT EXISTS tsv tsvector;

CREATE INDEX IF NOT EXISTS idx_articles_tsv ON articles USING GIN(tsv);

-- Обновление tsv при вставке и обновлении
CREATE OR REPLACE FUNCTION articles_tsv_trigger() RETURNS trigger AS $$
begin
  new.tsv := to_tsvector('russian', coalesce(new.title, '') || ' ' || coalesce(new.content, ''));
  return new;
end
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tsvectorupdate ON articles;
CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
ON articles FOR EACH ROW EXECUTE FUNCTION articles_tsv_trigger();


CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS article_likes (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_like BOOLEAN NOT NULL,  -- TRUE = лайк, FALSE = дизлайк
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (article_id, user_id)  -- один голос от одного пользователя
);


CREATE TABLE IF NOT EXISTS article_bookmarks (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (article_id, user_id)
);


CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, article_id)
);