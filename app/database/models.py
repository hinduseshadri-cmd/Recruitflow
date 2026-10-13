from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


# Table 1 — Candidates (main table)
class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name    = Column(String(200), nullable=True)
    email        = Column(String(200), unique=True, nullable=True)
    phone        = Column(String(50),  nullable=True)
    linkedin     = Column(Text, nullable=True)
    github       = Column(Text, nullable=True)
    portfolio    = Column(Text, nullable=True)
    address      = Column(Text, nullable=True)
    total_experience = Column(String(50), nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)

    # Relationships — links to other tables
    education    = relationship("Education",   back_populates="candidate", cascade="all, delete")
    experience   = relationship("Experience",  back_populates="candidate", cascade="all, delete")
    skills       = relationship("Skill",       back_populates="candidate", cascade="all, delete")
    ai_analysis  = relationship("AIAnalysis",  back_populates="candidate", cascade="all, delete")


# Table 2 — Education
class Education(Base):
    __tablename__ = "education"

    education_id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"), nullable=False)
    degree       = Column(String(200), nullable=True)
    institution  = Column(String(200), nullable=True)
    year         = Column(String(20),  nullable=True)
    cgpa         = Column(String(20),  nullable=True)

    candidate    = relationship("Candidate", back_populates="education")


# Table 3 — Experience
class Experience(Base):
    __tablename__ = "experience"

    experience_id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id  = Column(Integer, ForeignKey("candidates.candidate_id"), nullable=False)
    company_name  = Column(String(200), nullable=True)
    role          = Column(String(200), nullable=True)
    duration      = Column(String(100), nullable=True)
    description   = Column(Text, nullable=True)

    candidate     = relationship("Candidate", back_populates="experience")


# Table 4 — Skills
class Skill(Base):
    __tablename__ = "skills"

    skill_id     = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"), nullable=False)
    skill_name   = Column(String(200), nullable=True)
    skill_type   = Column(String(100), nullable=True)

    candidate    = relationship("Candidate", back_populates="skills")


# Table 5 — AI Analysis
class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    analysis_id              = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id             = Column(Integer, ForeignKey("candidates.candidate_id"), nullable=False)
    candidate_summary        = Column(Text, nullable=True)
    recommended_roles        = Column(Text, nullable=True)
    suitability_scores       = Column(Text, nullable=True)
    strengths                = Column(Text, nullable=True)
    domain                   = Column(String(200), nullable=True)
    top_skills               = Column(Text, nullable=True)

    # Advanced Scores
    technical_skills_score   = Column(Integer, nullable=True)
    experience_score         = Column(Integer, nullable=True)
    education_score          = Column(Integer, nullable=True)
    communication_score      = Column(Integer, nullable=True)
    overall_score            = Column(Integer, nullable=True)

    # Score Breakdown Reasons
    technical_skills_reason  = Column(Text, nullable=True)
    experience_reason        = Column(Text, nullable=True)
    education_reason         = Column(Text, nullable=True)
    communication_reason     = Column(Text, nullable=True)

    # Improvement Areas
    improvement_areas        = Column(Text, nullable=True)

    candidate                = relationship("Candidate", back_populates="ai_analysis")