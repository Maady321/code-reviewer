import logging
import asyncio
from uuid import UUID, uuid4
from datetime import datetime
from app.database.supabase_client import supabase
from app.services.ai_service import ai_service
from app.services.github_service import github_service
from app.utils.parser import is_supported_file

logger = logging.getLogger(__name__)

async def analyze_and_store_file(session_id: str, file_name: str, file_content: str):
    analysis_result = await ai_service.analyze_code(file_content)
    
    issues = analysis_result.get("issues", [])
    overall_score = analysis_result.get("score", 0.0)
    
    crit_count = 0
    results_to_insert = []
    
    for issue in issues:
        severity = issue.get("severity", "low")
        if severity.lower() == "critical":
            crit_count += 1
            
        results_to_insert.append({
            "id": str(uuid4()),
            "session_id": session_id,
            "file_name": file_name,
            "line_number": issue.get("line_number"),
            "severity": severity,
            "issue_type": issue.get("type", "unknown"),
            "description": issue.get("description", ""),
            "suggestion": issue.get("suggestion", "")
        })
        
    if results_to_insert:
        try:
            supabase.table("review_results").insert(results_to_insert).execute()
        except Exception as e:
            logger.error(f"Failed to insert review results into Supabase: {e}")
        
    return overall_score, len(issues), crit_count

async def async_process_repo_review(session_id: str, repo_url: str):
    try:
        files = await github_service.fetch_repo_files(repo_url)
        total_score, total_issues, total_critical = 0.0, 0, 0
        
        tasks = []
        analyzed_files = 0
        
        async def process_file(file):
            try:
                content = await github_service.fetch_file_content(repo_url, file["path"])
                score, issues, c_issues = await analyze_and_store_file(session_id, file["path"], content)
                return score, issues, c_issues
            except Exception as file_e:
                logger.error(f"Error processing file {file['path']}: {file_e}")
                return 0.0, 0, 0
                
        for file in files:
            if analyzed_files >= 3:
                break
            if is_supported_file(file["path"]):
                tasks.append(process_file(file))
                analyzed_files += 1

        results = await asyncio.gather(*tasks)
        
        for score, issues, c_issues in results:
            total_score += score
            total_issues += issues
            total_critical += c_issues

        avg_score = total_score / analyzed_files if analyzed_files > 0 else 0.0

        try:
            supabase.table("code_quality_scores").insert({
                "id": str(uuid4()),
                "session_id": session_id,
                "score": avg_score,
                "total_issues": total_issues,
                "critical_issues": total_critical
            }).execute()
        except Exception as e:
            logger.error(f"Failed to insert quality score into Supabase: {e}")
            
    except Exception as e:
        logger.error(f"Error processing repo {repo_url}: {e}")
        # Insert a fallback score so the UI stops polling forever
        try:
            supabase.table("code_quality_scores").insert({
                "id": str(uuid4()),
                "session_id": session_id,
                "score": 0.0,
                "total_issues": 1,
                "critical_issues": 1
            }).execute()
            
            supabase.table("review_results").insert({
                "id": str(uuid4()),
                "session_id": session_id,
                "file_name": "system",
                "severity": "critical",
                "issue_type": "error",
                "description": f"Failed to fetch repository files: {str(e)}"
            }).execute()
        except:
            pass

async def async_process_pr_review(session_id: str, pr_url: str):
    try:
        diff = await github_service.fetch_pr_diff(pr_url)
        score, issues, c_issues = await analyze_and_store_file(session_id, "pull_request.diff", diff)
        
        try:
            supabase.table("code_quality_scores").insert({
                "id": str(uuid4()),
                "session_id": session_id,
                "score": score,
                "total_issues": issues,
                "critical_issues": c_issues
            }).execute()
        except Exception as e:
            logger.error(f"Failed to insert quality score into Supabase: {e}")
            
    except Exception as e:
        logger.error(f"Error processing PR {pr_url}: {e}")

async def async_process_snippet(session_id: str, filename: str, code: str):
    try:
        score, issues, c_issues = await analyze_and_store_file(session_id, filename, code)
        
        try:
            supabase.table("code_quality_scores").insert({
                "id": str(uuid4()),
                "session_id": session_id,
                "score": score,
                "total_issues": issues,
                "critical_issues": c_issues
            }).execute()
        except Exception as e:
            logger.error(f"Failed to insert quality score into Supabase for snippet: {e}")
            
    except Exception as e:
        logger.error(f"Error processing snippet: {e}")
