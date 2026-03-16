import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Text, Uuid
from sqlalchemy.orm import relationship
from app.database.db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("ReviewSession", back_populates="user", cascade="all, delete")


class ReviewSession(Base):
    __tablename__ = "review_sessions"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"))
    repo_url = Column(String, nullable=True)
    commit_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")
    results = relationship("ReviewResult", back_populates="session", cascade="all, delete")
    score = relationship("CodeQualityScore", back_populates="session", uselist=False, cascade="all, delete")


class ReviewResult(Base):
    __tablename__ = "review_results"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(Uuid(as_uuid=True), ForeignKey("review_sessions.id"))
    file_name = Column(String, nullable=False)
    line_number = Column(Integer, nullable=True)
    severity = Column(String, nullable=False)
    issue_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    suggestion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ReviewSession", back_populates="results")


class CodeQualityScore(Base):
    __tablename__ = "code_quality_scores"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(Uuid(as_uuid=True), ForeignKey("review_sessions.id"))
    score = Column(Float, nullable=False)
    total_issues = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    
    session = relationship("ReviewSession", back_populates="score")
