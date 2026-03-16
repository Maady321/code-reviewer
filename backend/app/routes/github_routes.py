from fastapi import APIRouter

router = APIRouter(prefix="/github", tags=["github"])

@router.get("/status")
async def github_status():
    """Check if GitHub integration is available."""
    from app.config.settings import settings
    return {"configured": bool(settings.GITHUB_TOKEN)}
