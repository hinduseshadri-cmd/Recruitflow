from sqlalchemy.orm import Session
from app.database.models import Candidate, Education, Experience, Skill, AIAnalysis


# ─────────────────────────────────────────
# CHECK DUPLICATE
# ─────────────────────────────────────────

def check_duplicate(db: Session, email: str) -> bool:
    candidate = db.query(Candidate).filter(Candidate.email == email).first()
    return candidate is not None


# ─────────────────────────────────────────
# SAVE CANDIDATE
# ─────────────────────────────────────────

def save_candidate(db: Session, data: dict) -> Candidate:
    candidate = Candidate(
        full_name        = data.get("full_name"),
        email            = data.get("email"),
        phone            = data.get("phone"),
        linkedin         = data.get("linkedin"),
        github           = data.get("github"),
        portfolio        = data.get("portfolio"),
        address          = data.get("address"),
        total_experience = data.get("total_experience")
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


# ─────────────────────────────────────────
# SAVE EDUCATION
# ─────────────────────────────────────────

def save_education(db: Session, candidate_id: int, education_list: list):
    for edu in education_list:
        education = Education(
            candidate_id = candidate_id,
            degree       = edu.get("degree"),
            institution  = edu.get("institution"),
            year         = edu.get("year"),
            cgpa         = edu.get("cgpa")
        )
        db.add(education)
    db.commit()


# ─────────────────────────────────────────
# SAVE EXPERIENCE
# ─────────────────────────────────────────

def save_experience(db: Session, candidate_id: int, experience_list: list):
    for exp in experience_list:
        experience = Experience(
            candidate_id = candidate_id,
            company_name = exp.get("company_name"),
            role         = exp.get("role"),
            duration     = exp.get("duration"),
            description  = exp.get("description")
        )
        db.add(experience)
    db.commit()


# ─────────────────────────────────────────
# SAVE SKILLS
# ─────────────────────────────────────────

def save_skills(db: Session, candidate_id: int, skills_list: list):
    for skill in skills_list:
        skill_obj = Skill(
            candidate_id = candidate_id,
            skill_name   = skill.get("skill_name"),
            skill_type   = skill.get("skill_type")
        )
        db.add(skill_obj)
    db.commit()


# ─────────────────────────────────────────
# SAVE AI ANALYSIS
# ─────────────────────────────────────────

def save_ai_analysis(db: Session, candidate_id: int, ai_data: dict):
    analysis = AIAnalysis(
        candidate_id             = candidate_id,
        candidate_summary        = ai_data.get("candidate_summary"),
        recommended_roles        = ai_data.get("recommended_roles"),
        suitability_scores       = ai_data.get("suitability_scores"),
        strengths                = ai_data.get("strengths"),
        domain                   = ai_data.get("domain"),
        top_skills               = ai_data.get("top_skills"),
        technical_skills_score   = ai_data.get("technical_skills_score", 0),
        experience_score         = ai_data.get("experience_score", 0),
        education_score          = ai_data.get("education_score", 0),
        communication_score      = ai_data.get("communication_score", 0),
        overall_score            = ai_data.get("overall_score", 0),
        technical_skills_reason  = ai_data.get("technical_skills_reason"),
        experience_reason        = ai_data.get("experience_reason"),
        education_reason         = ai_data.get("education_reason"),
        communication_reason     = ai_data.get("communication_reason"),
        improvement_areas        = ai_data.get("improvement_areas")
    )
    db.add(analysis)
    db.commit()


# ─────────────────────────────────────────
# GET ALL CANDIDATES
# ─────────────────────────────────────────

def get_all_candidates(db: Session) -> list:
    return db.query(Candidate).all()


# ─────────────────────────────────────────
# GET CANDIDATE BY ID
# ─────────────────────────────────────────

def get_candidate_by_id(db: Session, candidate_id: int) -> Candidate:
    return db.query(Candidate).filter(
        Candidate.candidate_id == candidate_id
    ).first()


# ─────────────────────────────────────────
# GET AI ANALYSIS BY CANDIDATE ID
# ─────────────────────────────────────────

def get_ai_analysis(db: Session, candidate_id: int) -> AIAnalysis:
    return db.query(AIAnalysis).filter(
        AIAnalysis.candidate_id == candidate_id
    ).first()

# ─────────────────────────────────────────
# GET CANDIDATES RANKED BY OVERALL SCORE
# ─────────────────────────────────────────

def get_ranked_candidates(db: Session) -> list:
    results = db.query(Candidate, AIAnalysis)\
        .join(AIAnalysis, Candidate.candidate_id == AIAnalysis.candidate_id)\
        .order_by(AIAnalysis.overall_score.desc())\
        .all()

    ranked = []
    for rank, (candidate, analysis) in enumerate(results, start=1):
        ranked.append({
            "rank"                  : rank,
            "candidate_id"          : candidate.candidate_id,
            "full_name"             : candidate.full_name,
            "email"                 : candidate.email,
            "total_experience"      : candidate.total_experience,
            "domain"                : analysis.domain,
            "overall_score"         : analysis.overall_score,
            "technical_skills_score": analysis.technical_skills_score,
            "experience_score"      : analysis.experience_score,
            "education_score"       : analysis.education_score,
            "communication_score"   : analysis.communication_score,
            "recommended_roles"     : analysis.recommended_roles,
            "suitability_scores"    : analysis.suitability_scores,
            "improvement_areas"     : analysis.improvement_areas
        })

    return ranked