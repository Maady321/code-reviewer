from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from typing import List
from uuid import uuid4

from app.schemas.review_schema import RepoReviewRequest, PRReviewRequest, ReviewSessionSchema, ReviewSessionDetailSchema, SnippetReviewRequest
from app.core.dependencies import get_current_user
from app.services.review_service import analyze_and_store_file, async_process_repo_review, async_process_pr_review, async_process_snippet
from app.database.supabase_client import supabase
# Note: get_current_user returns a gotrue User which contains the 'id'

router = APIRouter(prefix="/review", tags=["review"])

@router.post("/file", response_model=dict, status_code=202)
async def upload_file_review(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    content = await file.read()
    content_str = content.decode("utf-8")
    
    session_id = str(uuid4())
    
    # Store session to Supabase
    try:
        supabase.table("review_sessions").insert({
            "id": session_id,
            "user_id": current_user.id,
            "repo_url": file.filename
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # We could do this dynamically inline, but we'll do it sequentially here for files.
    score, issues, c_issues = await analyze_and_store_file(session_id, file.filename, content_str)
    
    try:
        supabase.table("code_quality_scores").insert({
            "id": str(uuid4()),
            "session_id": session_id,
            "score": score,
            "total_issues": issues,
            "critical_issues": c_issues
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"message": "File processed successfully", "session_id": session_id}


@router.post("/repository", response_model=dict, status_code=202)
async def repository_review(
    req: RepoReviewRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    session_id = str(uuid4())
    
    try:
        supabase.table("review_sessions").insert({
            "id": session_id,
            "user_id": current_user.id,
            "repo_url": req.repo_url
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    background_tasks.add_task(async_process_repo_review, session_id, req.repo_url)
    
    return {"message": "Repository queued for review", "session_id": session_id}


@router.post("/pull-request", response_model=dict, status_code=202)
async def pr_review(
    req: PRReviewRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    session_id = str(uuid4())
    
    try:
        supabase.table("review_sessions").insert({
            "id": session_id,
            "user_id": current_user.id,
            "repo_url": req.pr_url
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    background_tasks.add_task(async_process_pr_review, session_id, req.pr_url)
    
    return {"message": "Pull Request queued for review", "session_id": session_id}


@router.post("/snippet", response_model=dict, status_code=202)
async def snippet_review(
    req: SnippetReviewRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    session_id = str(uuid4())
    filename = "pasted_snippet.txt" if not req.language else f"pasted_snippet.{req.language}"
    
    try:
        supabase.table("review_sessions").insert({
            "id": session_id,
            "user_id": current_user.id,
            "repo_url": "Pasted Code Snippet",
            "commit_hash": req.code
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # Queue up the background task
    background_tasks.add_task(async_process_snippet, session_id, filename, req.code)
    
    return {"message": "Snippet queued successfully", "session_id": session_id}


@router.get("/history")
async def get_history(current_user = Depends(get_current_user)):
    try:
        # We need to fetch sessions and their corresponding scores
        # We can either use a supabase join if FKs are set, or just run two queries.
        res = supabase.table("review_sessions") \
            .select("*") \
            .eq("user_id", current_user.id) \
            .order("created_at", desc=True) \
            .execute()
            
        sessions = res.data
        if not sessions:
            return []
            
        session_ids = [s["id"] for s in sessions]
        
        # Batch fetch scores
        scores_res = supabase.table("code_quality_scores") \
            .select("*") \
            .in_("session_id", session_ids) \
            .execute()
            
        scores_dict = {s["session_id"]: s for s in scores_res.data}
        
        for session in sessions:
            session["score_data"] = scores_dict.get(session["id"])
            
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}")
async def get_review_details(id: str, current_user = Depends(get_current_user)):
    # Verify session ownership
    try:
        session_res = supabase.table("review_sessions").select("*").eq("id", id).eq("user_id", current_user.id).execute()
        if not session_res.data:
            raise HTTPException(status_code=404, detail="Review session not found")
        
        session = session_res.data[0]
        
        # Load related data
        score_res = supabase.table("code_quality_scores").select("*").eq("session_id", id).execute()
        results_res = supabase.table("review_results").select("*").eq("session_id", id).execute()

        session["score"] = score_res.data[0] if score_res.data else None
        session["results"] = results_res.data if results_res.data else []
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
