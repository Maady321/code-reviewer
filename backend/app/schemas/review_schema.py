from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ReviewResultSchema(BaseModel):
    id: str
    file_name: str
    line_number: Optional[int]
    severity: str
    issue_type: str
    description: str
    suggestion: Optional[str]

    class Config:
        from_attributes = True

class CodeQualityScoreSchema(BaseModel):
    score: float
    total_issues: int
    critical_issues: int

    class Config:
        from_attributes = True

class ReviewSessionSchema(BaseModel):
    id: str
    user_id: str
    repo_url: Optional[str]
    commit_hash: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReviewSessionDetailSchema(ReviewSessionSchema):
    score: Optional[CodeQualityScoreSchema]
    results: List[ReviewResultSchema]
    
    class Config:
        from_attributes = True

class RepoReviewRequest(BaseModel):
    repo_url: str

class PRReviewRequest(BaseModel):
    pr_url: str

class SnippetReviewRequest(BaseModel):
    code: str
    language: Optional[str] = "python"
