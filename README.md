# 🧠 RecruitFlow Intelligence Engine

> AI-Powered Resume Parsing and Candidate Analysis System

---

## 📌 Overview

RecruitFlow Intelligence Engine is a backend system that automates initial resume screening using AI. It parses bulk resumes, extracts structured candidate information, stores it in a MySQL database, and uses AI-based analysis to determine suitable job roles and compatibility scores for candidates.

---

## 🎯 Objectives

- Extract resume information automatically
- Convert unstructured resumes into structured records
- Store candidate profiles in MySQL
- Use AI to understand skills and experiences
- Recommend relevant job roles
- Assign suitability percentages
- Reduce manual resume filtering effort

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Backend | Python 3.10+ |
| API Framework | FastAPI |
| Server | Uvicorn |
| AI Layer | Groq AI (LLaMA 3.3) |
| Database | MySQL 8.0 |
| ORM | SQLAlchemy |
| PDF Parsing | pdfplumber, PyMuPDF |
| DOCX Parsing | python-docx |
| Environment | Virtualenv |
| Frontend | HTML5, CSS3, Vanilla JS |

---

## 📁 Project Structure

```
recruitflow/
│
├── app/
│   ├── __init__.py
│   ├── ai_engine/
│   │   ├── __init__.py
│   │   └── gemini_wrapper.py      ← AI analysis (Groq)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py                  ← MySQL connection
│   │   ├── models.py              ← Table definitions
│   │   └── crud.py                ← Save and fetch data
│   ├── parser/
│   │   ├── __init__.py
│   │   └── resume_parser.py       ← PDF/DOCX parsing
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py              ← Upload API endpoint
│   │   └── candidates.py          ← Candidate API endpoints
│   ├── models/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
│
├── uploads/                       ← Uploaded resume files
├── dashboard.html                 ← HR Dashboard webpage
├── main.py                        ← App entry point
├── .env                           ← Secret credentials
├── requirements.txt               ← Python dependencies
└── README.md                      ← This file
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10 or above
- MySQL 8.0 or above
- Git (optional)

---

### Step 1 — Clone or Download the Project

```bash
cd C:\Users\YourName\Desktop
mkdir project_root
cd project_root
```

---

### Step 2 — Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows PowerShell:**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

---

### Step 3 — Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy pymysql cryptography pymupdf pdfplumber python-docx groq python-dotenv python-multipart aiofiles
```

Save dependencies:
```bash
pip freeze > requirements.txt
```

---

### Step 4 — Set Up MySQL Database

Open MySQL and create the database:
```sql
CREATE DATABASE recruitflow;
```

---

### Step 5 — Configure Environment Variables

Create a `.env` file in the root `recruitflow` folder:

```env
GEMINI_API_KEY=your_groq_api_key_here

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=recruitflow

UPLOAD_FOLDER=uploads
```

Get your Groq API key from: https://console.groq.com

---

### Step 6 — Run the Server

```bash
uvicorn main:app --reload
```

You should see:
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete
```

---

### Step 7 — Open the Dashboard

Double click `dashboard.html` in your project folder to open the HR Dashboard in your browser.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Welcome message |
| GET | /health | Health check |
| POST | /upload | Upload multiple resumes |
| GET | /candidates | Get all candidates |
| GET | /candidates/{id} | Get one candidate profile |
| GET | /candidates/{id}/analysis | Get AI analysis and scores |
| GET | /candidates-full-report | Get full report of all candidates |

---

## 📤 Upload Resumes

### Via Dashboard (Recommended)
1. Open `dashboard.html` in browser
2. Make sure server is running
3. Click Upload Resumes in sidebar
4. Drag and drop or click Choose Files
5. Select multiple PDF or DOCX resumes
6. Click Analyze with AI

### Via Postman
- Method: POST
- URL: `http://127.0.0.1:8000/upload`
- Body: form-data
- Key: `files` (type: File)
- Value: Select PDF or DOCX files

---

## 🗄️ Database Schema

### candidates
| Field | Type | Description |
|---|---|---|
| candidate_id | INT (PK) | Auto increment ID |
| full_name | VARCHAR | Candidate name |
| email | VARCHAR (UNIQUE) | Email address |
| phone | VARCHAR | Phone number |
| linkedin | TEXT | LinkedIn URL |
| github | TEXT | GitHub URL |
| portfolio | TEXT | Portfolio URL |
| address | TEXT | Address |
| total_experience | VARCHAR | Years of experience |
| created_at | DATETIME | Record creation time |

### education
| Field | Type | Description |
|---|---|---|
| education_id | INT (PK) | Auto increment ID |
| candidate_id | INT (FK) | Links to candidates |
| degree | VARCHAR | Degree name |
| institution | VARCHAR | College/University |
| year | VARCHAR | Year of completion |
| cgpa | VARCHAR | CGPA or percentage |

### experience
| Field | Type | Description |
|---|---|---|
| experience_id | INT (PK) | Auto increment ID |
| candidate_id | INT (FK) | Links to candidates |
| company_name | VARCHAR | Company name |
| role | VARCHAR | Job role/title |
| duration | VARCHAR | Employment period |
| description | TEXT | Job description |

### skills
| Field | Type | Description |
|---|---|---|
| skill_id | INT (PK) | Auto increment ID |
| candidate_id | INT (FK) | Links to candidates |
| skill_name | VARCHAR | Skill name |
| skill_type | VARCHAR | Technical or Soft |

### ai_analysis
| Field | Type | Description |
|---|---|---|
| analysis_id | INT (PK) | Auto increment ID |
| candidate_id | INT (FK) | Links to candidates |
| candidate_summary | TEXT | AI generated summary |
| recommended_roles | TEXT | Suggested job roles |
| suitability_scores | TEXT | Role match percentages |
| strengths | TEXT | Key strengths |
| domain | VARCHAR | Primary domain |
| top_skills | TEXT | Top skills identified |

---

## 🔄 API Workflow

```
Upload Resume
      ↓
Validate File Format (PDF/DOCX only)
      ↓
Save to uploads/ folder
      ↓
Extract Raw Text (pdfplumber / python-docx)
      ↓
Parse Structured Information
(name, email, phone, skills, education, experience)
      ↓
Check for Duplicate (by email)
      ↓
Save to MySQL Database
      ↓
Send Parsed Data to Groq AI
      ↓
Receive AI Insights
(summary, domain, roles, scores)
      ↓
Save AI Analysis to Database
      ↓
Return JSON Response
```

---

## ⚠️ Error Handling

| Error Scenario | Action Taken |
|---|---|
| Invalid file format | Rejected with error message |
| Corrupted PDF | Error logged, file skipped |
| AI API failure | Retry up to 3 times |
| Missing resume fields | Stored as null, processing continues |
| Duplicate resume | Flagged and skipped |

---

## 🚀 Running Commands

```bash
# Navigate to project
cd C:\Users\HINDU\Desktop\project_root\recruitflow

# Activate virtual environment
venv\Scripts\activate

# Start server
uvicorn main:app --reload

# Stop server
Ctrl + C
```

---

## 🔒 Security Notes

- Never share your `.env` file
- Never commit `.env` to Git
- Add `.env` to `.gitignore`
- Keep API keys private
- Use strong MySQL passwords

---

## 📋 Future Enhancements (Phase 2)

- Resume Ranking by score
- Candidate Search and Filter
- Skill Gap Detection
- Auto Email Shortlisting
- ATS Integration
- AI Interview Question Generator
- Resume Deduplication Engine
- Candidate Scoring Dashboard

---

## 👨‍💻 Developed By

RecruitFlow Intelligence Engine — Phase 1
Developed as part of intern development project.

---

## 📄 License

This project is intended for internal use only.
