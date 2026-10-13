from groq import Groq
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# CONNECT TO GROQ AI
# ─────────────────────────────────────────

client = Groq(api_key=os.getenv("GEMINI_API_KEY"))


# ─────────────────────────────────────────
# BUILD PROMPT FROM CANDIDATE DATA
# ─────────────────────────────────────────

def build_prompt(candidate_data: dict) -> str:
    skills = candidate_data.get("skills", [])
    skill_names = [s["skill_name"] for s in skills if isinstance(s, dict)]

    education = candidate_data.get("education", [])
    edu_text = ""
    for edu in education:
        if isinstance(edu, dict):
            edu_text += f"{edu.get('degree', '')} from {edu.get('institution', '')} "

    experience = candidate_data.get("experience", [])
    exp_text = ""
    for exp in experience:
        if isinstance(exp, dict):
            exp_text += f"{exp.get('role', '')} at {exp.get('company_name', '')} ({exp.get('duration', '')}). "

    return f"""
You are an expert HR recruiter and career analyst.
Analyze this candidate resume data carefully.
Return ONLY a valid JSON object. No extra text, no markdown.

Candidate Information:
- Name: {candidate_data.get('full_name', 'N/A')}
- Email: {candidate_data.get('email', 'N/A')}
- Total Experience: {candidate_data.get('total_experience', 'N/A')}
- Skills: {', '.join(skill_names[:15]) if skill_names else 'N/A'}
- Education: {edu_text[:200] if edu_text else 'N/A'}
- Experience: {exp_text[:300] if exp_text else 'N/A'}
- Projects: {str(candidate_data.get('projects', []))[:200]}
- Certifications: {str(candidate_data.get('certifications', []))[:200]}

Return EXACTLY this JSON format:
{{
    "candidate_summary": "2-3 sentence professional summary",
    "domain": "Primary domain like Backend Development, Data Science etc.",
    "top_skills": ["skill1", "skill2", "skill3"],
    "strengths": "Key strengths in 1-2 sentences",
    "recommended_roles": [
        {{"role": "Job Role 1", "suitability_score": 90}},
        {{"role": "Job Role 2", "suitability_score": 82}},
        {{"role": "Job Role 3", "suitability_score": 75}}
    ],
    "advanced_scores": {{
        "technical_skills_score": 85,
        "experience_score": 70,
        "education_score": 80,
        "communication_score": 75,
        "overall_score": 78
    }},
    "score_breakdown": {{
        "technical_skills_reason": "One sentence reason for technical score",
        "experience_reason": "One sentence reason for experience score",
        "education_reason": "One sentence reason for education score",
        "communication_reason": "One sentence reason for communication score"
    }},
    "improvement_areas": ["area1", "area2", "area3"]
}}
"""


# ─────────────────────────────────────────
# SEND TO GROQ AND GET RESPONSE
# ─────────────────────────────────────────

def analyze_candidate(candidate_data: dict) -> dict:
    prompt = build_prompt(candidate_data)
    max_retries = 3

    for attempt in range(max_retries):
        try:
            print(f"  Sending to Groq AI... (attempt {attempt + 1})")

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR recruiter. Always respond with valid JSON only. No markdown, no extra text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )

            raw_text = response.choices[0].message.content.strip()
            print(f"  Raw response preview: {raw_text[:100]}")

            # Clean markdown if added
            if "```" in raw_text:
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            raw_text = raw_text.strip()

            result = json.loads(raw_text)
            print(f"  Groq AI analysis complete!")
            return result

        except json.JSONDecodeError as e:
            print(f"  Attempt {attempt + 1}: Invalid JSON — {str(e)}")
            time.sleep(2)

        except Exception as e:
            print(f"  Attempt {attempt + 1}: Groq API error — {str(e)}")
            time.sleep(3)

    print("  All retries failed. Returning empty analysis.")
    return {
        "candidate_summary"  : "Analysis unavailable",
        "domain"             : "Unknown",
        "top_skills"         : [],
        "strengths"          : "N/A",
        "recommended_roles"  : [],
        "advanced_scores"    : {
            "technical_skills_score": 0,
            "experience_score"      : 0,
            "education_score"       : 0,
            "communication_score"   : 0,
            "overall_score"         : 0
        },
        "score_breakdown"    : {
            "technical_skills_reason": "N/A",
            "experience_reason"      : "N/A",
            "education_reason"       : "N/A",
            "communication_reason"   : "N/A"
        },
        "improvement_areas"  : []
    }


# ─────────────────────────────────────────
# FORMAT RESULT FOR DATABASE
# ─────────────────────────────────────────

def format_for_database(ai_result: dict) -> dict:
    roles = ai_result.get("recommended_roles", [])

    roles_string = ", ".join(
        [r["role"] for r in roles if isinstance(r, dict)]
    )

    scores_string = ", ".join(
        [f"{r['role']}: {r['suitability_score']}%"
         for r in roles if isinstance(r, dict)]
    )

    top_skills = ai_result.get("top_skills", [])
    skills_string = ", ".join(top_skills) if isinstance(top_skills, list) else str(top_skills)

    # Advanced scores
    adv = ai_result.get("advanced_scores", {})
    breakdown = ai_result.get("score_breakdown", {})
    improvements = ai_result.get("improvement_areas", [])

    return {
        "candidate_summary"       : ai_result.get("candidate_summary", ""),
        "recommended_roles"       : roles_string,
        "suitability_scores"      : scores_string,
        "strengths"               : ai_result.get("strengths", ""),
        "domain"                  : ai_result.get("domain", ""),
        "top_skills"              : skills_string,
        "technical_skills_score"  : adv.get("technical_skills_score", 0),
        "experience_score"        : adv.get("experience_score", 0),
        "education_score"         : adv.get("education_score", 0),
        "communication_score"     : adv.get("communication_score", 0),
        "overall_score"           : adv.get("overall_score", 0),
        "technical_skills_reason" : breakdown.get("technical_skills_reason", ""),
        "experience_reason"       : breakdown.get("experience_reason", ""),
        "education_reason"        : breakdown.get("education_reason", ""),
        "communication_reason"    : breakdown.get("communication_reason", ""),
        "improvement_areas"       : ", ".join(improvements) if isinstance(improvements, list) else str(improvements)
    }