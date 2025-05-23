from .auth import router as auth_router
from .products import router as products_router
from .categories import router as categories_router
from .article_images import router as article_images_router
from .articles import router as articles_router
from .upload import router as upload_router
from .profile import router as profile_router
from .bookmarks import router as bookmarks_router
from .comments import router as comments_router
from .likes import router as likes_router
from .users import router as users_router
from .favorites import router as favorites_router

all_routers = [
    auth_router,
    products_router,
    categories_router,
    article_images_router,
    articles_router,
    upload_router,
    profile_router,
    bookmarks_router,
    comments_router,
    likes_router,
    users_router,
    favorites_router,
]

