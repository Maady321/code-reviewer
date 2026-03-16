import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes, review_routes, github_routes

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Supabase handles DB migrations natively via GUI or CLI.
    # No SQLAlchemy operations needed on startup anymore!
    yield

app = FastAPI(
    title="AI Code Reviewer API (Supabase Edition)",
    description="Automated AI code review feedback.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(review_routes.router)
app.include_router(github_routes.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
