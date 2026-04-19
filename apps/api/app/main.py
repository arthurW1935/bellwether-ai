from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import brief, companies, discover, health, watchlist
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.services.bootstrap_service import bootstrap_service


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(discover.router)
app.include_router(watchlist.router)
app.include_router(brief.router)
app.include_router(companies.router)

register_exception_handlers(app)


@app.on_event("startup")
async def on_startup() -> None:
    bootstrap_service.initialize()
