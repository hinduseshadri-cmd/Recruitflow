from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database import crud
from fastapi.responses import StreamingResponse
import csv
import io
from app.database.models import Skill
from app.database.models import Candidate, Education, Experience, Skill, AIAnalysis
router = APIRouter()
from pydantic import BaseModel
from app.ai_engine.gemini_wrapper import client as groq_client
import json as json_lib


# ─────────────────────────────────────────
# GET ALL CANDIDATES
# ─────────────────────────────────────────

@router.get("/candidates")
def get_all_candidates(db: Session = Depends(get_db)):
    candidates = crud.get_all_candidates(db)

    if not candidates:
        return {
            "message"   : "No candidates found",
            "total"     : 0,
            "candidates": []
        }

    result = []
    for c in candidates:
        result.append({
            "candidate_id"    : c.candidate_id,
            "full_name"       : c.full_name,
            "email"           : c.email,
            "phone"           : c.phone,
            "linkedin"        : c.linkedin,
            "github"          : c.github,
            "total_experience": c.total_experience,
            "created_at"      : str(c.created_at)
        })

    return {
        "total"     : len(result),
        "candidates": result
    }


# ─────────────────────────────────────────
# GET SINGLE CANDIDATE BY ID
# ─────────────────────────────────────────

@router.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = crud.get_candidate_by_id(db, candidate_id)

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate with ID {candidate_id} not found"
        )

    # Get education records
    education = []
    for edu in candidate.education:
        education.append({
            "degree"     : edu.degree,
            "institution": edu.institution,
            "year"       : edu.year,
            "cgpa"       : edu.cgpa
        })

    # Get experience records
    experience = []
    for exp in candidate.experience:
        experience.append({
            "company_name": exp.company_name,
            "role"        : exp.role,
            "duration"    : exp.duration,
            "description" : exp.description
        })

    # Get skills
    skills = []
    for skill in candidate.skills:
        skills.append({
            "skill_name": skill.skill_name,
            "skill_type": skill.skill_type
        })

    return {
        "candidate_id"    : candidate.candidate_id,
        "full_name"       : candidate.full_name,
        "email"           : candidate.email,
        "phone"           : candidate.phone,
        "linkedin"        : candidate.linkedin,
        "github"          : candidate.github,
        "portfolio"       : candidate.portfolio,
        "address"         : candidate.address,
        "total_experience": candidate.total_experience,
        "created_at"      : str(candidate.created_at),
        "education"       : education,
        "experience"      : experience,
        "skills"          : skills
    }


# ─────────────────────────────────────────
# GET AI ANALYSIS BY CANDIDATE ID
# ─────────────────────────────────────────

@router.get("/candidates/{candidate_id}/analysis")
def get_candidate_analysis(candidate_id: int, db: Session = Depends(get_db)):
    candidate = crud.get_candidate_by_id(db, candidate_id)

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate with ID {candidate_id} not found"
        )

    analysis = crud.get_ai_analysis(db, candidate_id)

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"No AI analysis found for candidate ID {candidate_id}"
        )

    return {
        "candidate_id"     : candidate_id,
        "full_name"        : candidate.full_name,
        "email"            : candidate.email,
        "candidate_summary": analysis.candidate_summary,
        "domain"           : analysis.domain,
        "top_skills"       : analysis.top_skills,
        "strengths"        : analysis.strengths,
        "recommended_roles": analysis.recommended_roles,
        "suitability_scores": analysis.suitability_scores
    }


# ─────────────────────────────────────────
# GET ALL CANDIDATES WITH THEIR ANALYSIS
# ─────────────────────────────────────────

@router.get("/candidates-full-report")
def get_full_report(db: Session = Depends(get_db)):
    candidates = crud.get_all_candidates(db)

    if not candidates:
        return {
            "message": "No candidates found",
            "total"  : 0,
            "report" : []
        }

    report = []
    for c in candidates:
        analysis = crud.get_ai_analysis(db, c.candidate_id)

        report.append({
            "candidate_id"     : c.candidate_id,
            "full_name"        : c.full_name,
            "email"            : c.email,
            "total_experience" : c.total_experience,
            "domain"           : analysis.domain if analysis else "N/A",
            "recommended_roles": analysis.recommended_roles if analysis else "N/A",
            "suitability_scores": analysis.suitability_scores if analysis else "N/A",
            "strengths"        : analysis.strengths if analysis else "N/A",
            "candidate_summary": analysis.candidate_summary if analysis else "N/A"
        })

    return {
        "total" : len(report),
        "report": report
    }

# ─────────────────────────────────────────
# GET RANKED CANDIDATES BY OVERALL SCORE
# ─────────────────────────────────────────

@router.get("/candidates-ranked")
def get_ranked_candidates(db: Session = Depends(get_db)):
    ranked = crud.get_ranked_candidates(db)

    if not ranked:
        return {
            "message": "No candidates found",
            "total"  : 0,
            "ranked" : []
        }

    return {
        "total" : len(ranked),
        "ranked": ranked
    }


# ─────────────────────────────────────────
# GET ADVANCED SCORES FOR ONE CANDIDATE
# ─────────────────────────────────────────

@router.get("/candidates/{candidate_id}/scores")
def get_candidate_scores(candidate_id: int, db: Session = Depends(get_db)):
    candidate = crud.get_candidate_by_id(db, candidate_id)

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate with ID {candidate_id} not found"
        )

    analysis = crud.get_ai_analysis(db, candidate_id)

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for candidate ID {candidate_id}"
        )

    return {
        "candidate_id"           : candidate_id,
        "full_name"              : candidate.full_name,
        "email"                  : candidate.email,
        "domain"                 : analysis.domain,
        "overall_score"          : analysis.overall_score,
        "advanced_scores"        : {
            "technical_skills_score": analysis.technical_skills_score,
            "experience_score"      : analysis.experience_score,
            "education_score"       : analysis.education_score,
            "communication_score"   : analysis.communication_score,
            "overall_score"         : analysis.overall_score
        },
        "score_breakdown"        : {
            "technical_skills_reason": analysis.technical_skills_reason,
            "experience_reason"      : analysis.experience_reason,
            "education_reason"       : analysis.education_reason,
            "communication_reason"   : analysis.communication_reason
        },
        "improvement_areas"      : analysis.improvement_areas,
        "recommended_roles"      : analysis.recommended_roles,
        "suitability_scores"     : analysis.suitability_scores
    }

# ─────────────────────────────────────────
# SEARCH AND FILTER CANDIDATES
# ─────────────────────────────────────────

@router.get("/candidates-search")
def search_candidates(
    name      : str = None,
    email     : str = None,
    domain    : str = None,
    min_score : int = None,
    max_score : int = None,
    skill     : str = None,
    experience: str = None,
    db        : Session = Depends(get_db)
):
    # Get all candidates first
    candidates = crud.get_all_candidates(db)
    results = []

    for c in candidates:
        analysis = crud.get_ai_analysis(db, c.candidate_id)

        # Filter by name
        if name:
            if not c.full_name:
                continue
            if name.lower() not in c.full_name.lower():
                continue

        # Filter by email
        if email:
            if not c.email:
                continue
            if email.lower() not in c.email.lower():
                continue

        # Filter by domain
        if domain:
            if not analysis or not analysis.domain:
                continue
            if domain.lower() not in analysis.domain.lower():
                continue

        # Filter by minimum score
        if min_score is not None:
            if not analysis or not analysis.overall_score:
                continue
            if analysis.overall_score < min_score:
                continue

        # Filter by maximum score
        if max_score is not None:
            if not analysis or not analysis.overall_score:
                continue
            if analysis.overall_score > max_score:
                continue

        # Filter by experience
        if experience:
            if not c.total_experience:
                continue
            if experience.lower() not in c.total_experience.lower():
                continue

        # Filter by skill
        if skill:
            candidate_skills = db.query(Skill).filter(
                Skill.candidate_id == c.candidate_id,
                Skill.skill_name.ilike(f"%{skill}%")
            ).first()
            if not candidate_skills:
                continue

        # Passed all filters — add to results
        results.append({
            "candidate_id"     : c.candidate_id,
            "full_name"        : c.full_name,
            "email"            : c.email,
            "total_experience" : c.total_experience,
            "domain"           : analysis.domain if analysis else "N/A",
            "overall_score"    : analysis.overall_score if analysis else 0,
            "recommended_roles": analysis.recommended_roles if analysis else "N/A",
            "suitability_scores": analysis.suitability_scores if analysis else "N/A"
        })

    # Sort by overall score descending
    results.sort(key=lambda x: x["overall_score"] or 0, reverse=True)

    return {
        "total"  : len(results),
        "filters": {
            "name"      : name,
            "domain"    : domain,
            "min_score" : min_score,
            "max_score" : max_score,
            "skill"     : skill,
            "experience": experience
        },
        "results": results
    }
# ─────────────────────────────────────────
# EXPORT ALL CANDIDATES AS CSV
# ─────────────────────────────────────────

@router.get("/export-candidates-csv")
def export_candidates_csv(db: Session = Depends(get_db)):
    candidates = crud.get_all_candidates(db)

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        "Rank",
        "Candidate ID",
        "Full Name",
        "Email",
        "Phone",
        "Total Experience",
        "Domain",
        "Overall Score",
        "Technical Skills Score",
        "Experience Score",
        "Education Score",
        "Recommended Roles",
        "Top Skills",
        "Strengths",
        "Improvement Areas",
        "LinkedIn",
        "GitHub"
    ])

    # Sort by overall score
    candidate_data = []
    for c in candidates:
        analysis = crud.get_ai_analysis(db, c.candidate_id)
        candidate_data.append((c, analysis))

    candidate_data.sort(
        key=lambda x: x[1].overall_score if x[1] else 0,
        reverse=True
    )

    # Data rows
    for rank, (c, analysis) in enumerate(candidate_data, start=1):
        writer.writerow([
            rank,
            c.candidate_id,
            c.full_name or "",
            c.email or "",
            c.phone or "",
            c.total_experience or "",
            analysis.domain if analysis else "",
            analysis.overall_score if analysis else "",
            analysis.technical_skills_score if analysis else "",
            analysis.experience_score if analysis else "",
            analysis.education_score if analysis else "",
            analysis.recommended_roles if analysis else "",
            analysis.top_skills if analysis else "",
            analysis.strengths if analysis else "",
            analysis.improvement_areas if analysis else "",
            c.linkedin or "",
            c.github or ""
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=recruitflow_candidates.csv"
        }
    )


# ─────────────────────────────────────────
# EXPORT RANKED CANDIDATES AS CSV
# ─────────────────────────────────────────

@router.get("/export-ranked-csv")
def export_ranked_csv(db: Session = Depends(get_db)):
    ranked = crud.get_ranked_candidates(db)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Rank",
        "Candidate ID",
        "Full Name",
        "Email",
        "Domain",
        "Overall Score",
        "Technical Skills Score",
        "Experience Score",
        "Education Score",
        "Total Experience",
        "Recommended Roles",
        "Improvement Areas"
    ])

    for r in ranked:
        writer.writerow([
            r["rank"],
            r["candidate_id"],
            r["full_name"] or "",
            r["email"] or "",
            r["domain"] or "",
            r["overall_score"] or "",
            r["technical_skills_score"] or "",
            r["experience_score"] or "",
            r["education_score"] or "",
            r["total_experience"] or "",
            r["recommended_roles"] or "",
            r["improvement_areas"] or ""
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=recruitflow_ranked.csv"
        }
    )


# ─────────────────────────────────────────
# EXPORT ONE CANDIDATE AS CSV
# ─────────────────────────────────────────

@router.get("/export-candidate-csv/{candidate_id}")
def export_candidate_csv(candidate_id: int, db: Session = Depends(get_db)):
    candidate = crud.get_candidate_by_id(db, candidate_id)

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    analysis = crud.get_ai_analysis(db, candidate_id)

    output = io.StringIO()
    writer = csv.writer(output)

    # Candidate info
    writer.writerow(["Field", "Value"])
    writer.writerow(["Full Name", candidate.full_name or ""])
    writer.writerow(["Email", candidate.email or ""])
    writer.writerow(["Phone", candidate.phone or ""])
    writer.writerow(["Total Experience", candidate.total_experience or ""])
    writer.writerow(["LinkedIn", candidate.linkedin or ""])
    writer.writerow(["GitHub", candidate.github or ""])
    writer.writerow([])

    # AI Analysis
    if analysis:
        writer.writerow(["AI Analysis", ""])
        writer.writerow(["Domain", analysis.domain or ""])
        writer.writerow(["Overall Score", analysis.overall_score or ""])
        writer.writerow(["Technical Skills Score", analysis.technical_skills_score or ""])
        writer.writerow(["Experience Score", analysis.experience_score or ""])
        writer.writerow(["Education Score", analysis.education_score or ""])
        writer.writerow(["Candidate Summary", analysis.candidate_summary or ""])
        writer.writerow(["Top Skills", analysis.top_skills or ""])
        writer.writerow(["Strengths", analysis.strengths or ""])
        writer.writerow(["Recommended Roles", analysis.recommended_roles or ""])
        writer.writerow(["Improvement Areas", analysis.improvement_areas or ""])

    output.seek(0)
    name = (candidate.full_name or "candidate").replace(" ", "_")
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={name}_report.csv"
        }
    )
from pydantic import BaseModel
from app.ai_engine.gemini_wrapper import client as groq_client
import json as json_lib


class JobDescriptionInput(BaseModel):
    description: str


# ─────────────────────────────────────────
# EXTRACT REQUIRED SKILLS FROM JOB DESCRIPTION
# ─────────────────────────────────────────

@router.post("/extract-job-requirements")
def extract_job_requirements(payload: JobDescriptionInput):
    description = payload.description.strip()

    if not description or len(description) < 30:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short to analyze"
        )

    prompt = f"""
You are an expert technical recruiter. Read this job description and extract structured requirements.

Job Description:
{description[:3000]}

Return ONLY a valid JSON object, no extra text, no markdown, exactly in this format:
{{
    "required_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
    "min_experience_years": 3,
    "suggested_domain": "Backend Development",
    "summary": "1-2 sentence summary of what this role needs"
}}

Rules:
- required_skills: list only concrete technical skills, tools, languages, frameworks mentioned or clearly implied (max 10, lowercase not required)
- min_experience_years: a single number representing minimum years of experience required. If not mentioned, estimate based on seniority words (e.g. "Manager" or "Senior" implies 5+, "Engineer II" implies 2-3, no seniority implies 0)
- suggested_domain: pick ONE from exactly this list: Backend Development, Frontend Development, Full Stack Development, Data Science, Machine Learning, DevOps, Mobile Development, Cloud Computing, Data Analytics, Cybersecurity, UI/UX Design, QA/Testing
- summary: a short plain-English summary of what this role is looking for
"""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical recruiter. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=600
            )

            raw_text = response.choices[0].message.content.strip()

            if "```" in raw_text:
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            raw_text = raw_text.strip()

            result = json_lib.loads(raw_text)

            return {
                "required_skills"     : result.get("required_skills", []),
                "min_experience_years": result.get("min_experience_years", 0),
                "suggested_domain"    : result.get("suggested_domain", ""),
                "summary"             : result.get("summary", "")
            }

        except json_lib.JSONDecodeError:
            continue
        except Exception as e:
            print(f"Job extraction error (attempt {attempt + 1}): {str(e)}")
            continue

    raise HTTPException(
        status_code=500,
        detail="AI could not analyze this job description after multiple attempts"
    )