import os
from celery import Celery
from app.config.settings import settings
import asyncio

celery_app = Celery(
    "reviewer_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.task_routes = {
    "app.workers.tasks.process_repo_review": "main-queue",
    "app.workers.tasks.process_pr_review": "main-queue"
}

@celery_app.task(bind=True)
def process_repo_review(self, session_id: str, repo_url: str):
    # In a real async worker, we'd initialize DB session here, fetch files using GitHubService, 
    # analyze with AIService, and store results to DB.
    # We use a sync wrapper to run our async logic.
    from app.services.review_service import process_repo_review_sync
    process_repo_review_sync(session_id, repo_url)
    return f"Processed {repo_url} for session {session_id}"

@celery_app.task(bind=True)
def process_pr_review(self, session_id: str, pr_url: str):
    from app.services.review_service import process_pr_review_sync
    process_pr_review_sync(session_id, pr_url)
    return f"Processed PR {pr_url} for session {session_id}"
