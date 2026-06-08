from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import allievi, insegnanti, corsi, pagamenti, dashboard

app = FastAPI(
    title="Arsis API",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(allievi.router,     prefix="/api/v1/allievi",     tags=["allievi"])
app.include_router(insegnanti.router,  prefix="/api/v1/insegnanti",  tags=["insegnanti"])
app.include_router(corsi.router,       prefix="/api/v1/corsi",       tags=["corsi"])
app.include_router(pagamenti.router,   prefix="/api/v1/pagamenti",   tags=["pagamenti"])
app.include_router(dashboard.router,   prefix="/api/v1/dashboard",   tags=["dashboard"])


@app.get("/health")
async def health():
    return {"status": "ok"}
