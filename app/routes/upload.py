import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.database import crud
from app.parser.resume_parser import parse_resume
from app.ai_engine.gemini_wrapper import analyze_candidate, format_for_database

router = APIRouter()

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


# ─────────────────────────────────────────
# UPLOAD MULTIPLE RESUMES
# ─────────────────────────────────────────

@router.post("/upload")
async def upload_resumes(
    files: List[UploadFile] = File(description="Upload PDF or DOCX resumes"),
    db: Session = Depends(get_db)
):
    results = []

    for file in files:
        file_result = {
            "filename": file.filename,
            "status"  : "",
            "message" : ""
        }

        try:
            # Step 1 — Validate file extension
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                file_result["status"]  = "rejected"
                file_result["message"] = "Invalid format. Only PDF and DOCX allowed."
                results.append(file_result)
                continue

            # Step 2 — Save file to uploads folder
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            print(f"Saved: {file.filename}")

            # Step 3 — Parse the resume
            print(f"Parsing: {file.filename}")
            parsed_data = parse_resume(file_path)

            if "error" in parsed_data:
                file_result["status"]  = "failed"
                file_result["message"] = parsed_data["error"]
                results.append(file_result)
                continue

            # Step 4 — Check for duplicate
            email = parsed_data.get("email")
            if email and crud.check_duplicate(db, email):
                file_result["status"]  = "duplicate"
                file_result["message"] = f"Candidate with email {email} already exists."
                results.append(file_result)
                continue

            # Step 5 — Save candidate to database
            print(f"Saving candidate: {parsed_data.get('full_name')}")
            candidate = crud.save_candidate(db, parsed_data)

            # Step 6 — Save education records
            if parsed_data.get("education"):
                crud.save_education(
                    db,
                    candidate.candidate_id,
                    parsed_data["education"]
                )

            # Step 7 — Save experience records
            if parsed_data.get("experience"):
                crud.save_experience(
                    db,
                    candidate.candidate_id,
                    parsed_data["experience"]
                )

            # Step 8 — Save skills
            if parsed_data.get("skills"):
                crud.save_skills(
                    db,
                    candidate.candidate_id,
                    parsed_data["skills"]
                )

            # Step 9 — Send to Gemini AI for analysis
            print(f"Analyzing with Gemini AI: {parsed_data.get('full_name')}")
            ai_result = analyze_candidate(parsed_data)
            db_ready  = format_for_database(ai_result)

            # Step 10 — Save AI analysis
            crud.save_ai_analysis(
                db,
                candidate.candidate_id,
                db_ready
            )

            file_result["status"]       = "success"
            file_result["message"]      = "Resume processed successfully"
            file_result["candidate_id"] = candidate.candidate_id
            file_result["name"]         = parsed_data.get("full_name")
            file_result["email"]        = parsed_data.get("email")
            file_result["roles"]        = db_ready.get("recommended_roles")
            file_result["scores"]       = db_ready.get("suitability_scores")

        except Exception as e:
            file_result["status"]  = "error"
            file_result["message"] = f"Unexpected error: {str(e)}"
            print(f"Error processing {file.filename}: {str(e)}")

        results.append(file_result)

    # Summary
    total     = len(results)
    success   = len([r for r in results if r["status"] == "success"])
    failed    = len([r for r in results if r["status"] == "failed"])
    duplicate = len([r for r in results if r["status"] == "duplicate"])
    rejected  = len([r for r in results if r["status"] == "rejected"])

    return JSONResponse(content={
        "summary": {
            "total_uploaded": total,
            "successful"    : success,
            "failed"        : failed,
            "duplicates"    : duplicate,
            "rejected"      : rejected
        },
        "results": results
    })