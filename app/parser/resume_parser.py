import pdfplumber
import docx
import re
import os


# ─────────────────────────────────────────
# MAIN FUNCTION — CALL THIS FOR EACH RESUME
# ─────────────────────────────────────────

def parse_resume(file_path: str) -> dict:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        text = extract_text_from_docx(file_path)
    else:
        return {"error": "Unsupported file format"}

    if not text:
        return {"error": "Could not extract text from file"}

    print(f"Extracted text preview: {text[:200]}")
    return extract_information(text)


# ─────────────────────────────────────────
# EXTRACT TEXT FROM PDF
# ─────────────────────────────────────────

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text


# ─────────────────────────────────────────
# EXTRACT TEXT FROM DOCX
# ─────────────────────────────────────────

def extract_text_from_docx(file_path: str) -> str:
    text = ""
    try:
        doc = docx.Document(file_path)

        # Read normal paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"

        # Read text inside tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text += cell.text + "\n"

        # Read text inside shapes
        for shape in doc.inline_shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    if para.text.strip():
                        text += para.text + "\n"

    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text


# ─────────────────────────────────────────
# EXTRACT ALL INFORMATION FROM TEXT
# ─────────────────────────────────────────

def extract_information(text: str) -> dict:
    return {
        "full_name"        : extract_name(text),
        "email"            : extract_email(text),
        "phone"            : extract_phone(text),
        "linkedin"         : extract_linkedin(text),
        "github"           : extract_github(text),
        "portfolio"        : extract_portfolio(text),
        "skills"           : extract_skills(text),
        "education"        : extract_education(text),
        "experience"       : extract_experience(text),
        "total_experience" : extract_total_experience(text),
        "projects"         : extract_projects(text),
        "certifications"   : extract_certifications(text),
        "raw_text"         : text
    }


# ─────────────────────────────────────────
# EXTRACT NAME
# ─────────────────────────────────────────

def extract_name(text: str) -> str:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:10]:
        # Skip lines with special characters
        if re.search(r'[@|http|linkedin|github|phone|email|mobile|profile]',
                     line.lower()):
            continue
        # Skip lines that are just numbers
        if re.match(r'^[\d\s\+\-\(\)]+$', line):
            continue
        # Skip very long lines
        if len(line) > 60:
            continue
        # Skip lines with only one word that looks like a section header
        if len(line.split()) == 1 and line.isupper():
            continue
        # Skip lines with job titles or locations
        if re.search(r'developer|engineer|designer|analyst|manager|'
                     r'hosur|tamil|nadu|kerala|bangalore|chennai|'
                     r'profile|summary|objective',
                     line.lower()):
            continue
        # Accept names with at least 2 characters
        if len(line) >= 2:
            return line.title()
    # If nothing found try first line directly
    if lines:
        first_line = lines[0].strip()
        if len(first_line) >= 2:
            return first_line.title()
    return "Unknown"


# ─────────────────────────────────────────
# EXTRACT EMAIL
# ─────────────────────────────────────────

def extract_email(text: str) -> str:
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


# ─────────────────────────────────────────
# EXTRACT PHONE
# ─────────────────────────────────────────

def extract_phone(text: str) -> str:
    pattern = r'(\+?\d{1,3}[\s\-]?)?(\(?\d{3}\)?[\s\-]?)(\d{3}[\s\-]?\d{4})'
    match = re.search(pattern, text)
    return match.group(0).strip() if match else None


# ─────────────────────────────────────────
# EXTRACT LINKEDIN
# ─────────────────────────────────────────

def extract_linkedin(text: str) -> str:
    pattern = r'linkedin\.com/in/[a-zA-Z0-9\-\_]+'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


# ─────────────────────────────────────────
# EXTRACT GITHUB
# ─────────────────────────────────────────

def extract_github(text: str) -> str:
    pattern = r'github\.com/[a-zA-Z0-9\-\_]+'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


# ─────────────────────────────────────────
# EXTRACT PORTFOLIO
# ─────────────────────────────────────────

def extract_portfolio(text: str) -> str:
    pattern = r'(https?://(?!linkedin|github)[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}[^\s]*)'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


# ─────────────────────────────────────────
# EXTRACT SKILLS
# ─────────────────────────────────────────

def extract_skills(text: str) -> list:
    technical_skills = [
        "python", "java", "javascript", "typescript", "c++", "c#", "php",
        "ruby", "swift", "kotlin", "go", "rust", "scala", "r",
        "react", "angular", "vue", "nodejs", "django", "flask", "fastapi",
        "spring", "laravel", "express",
        "mysql", "postgresql", "mongodb", "sqlite", "redis", "oracle",
        "aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
        "git", "github", "gitlab", "linux", "bash",
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "pandas", "numpy", "scikit-learn", "opencv",
        "html", "css", "bootstrap", "tailwind",
        "rest api", "graphql", "microservices", "devops", "ci/cd",
        "android", "ios", "flutter", "react native",
        "selenium", "postman", "jira", "figma",
        "excel", "powerpoint", "word", "tableau", "power bi"
    ]

    soft_skills = [
        "communication", "teamwork", "leadership", "problem solving",
        "critical thinking", "time management", "adaptability",
        "creativity", "collaboration", "project management",
        "attention to detail", "multitasking", "analytical"
    ]

    found_skills = []
    text_lower = text.lower()

    for skill in technical_skills:
        if skill in text_lower:
            found_skills.append({
                "skill_name": skill.title(),
                "skill_type": "Technical"
            })

    for skill in soft_skills:
        if skill in text_lower:
            found_skills.append({
                "skill_name": skill.title(),
                "skill_type": "Soft"
            })

    return found_skills


# ─────────────────────────────────────────
# EXTRACT EDUCATION
# ─────────────────────────────────────────

def extract_education(text: str) -> list:
    education_list = []
    lines = text.split("\n")
    education_section = False

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Detect education section
        if re.search(r'^(education|academic|qualification)',
                     line, re.IGNORECASE):
            education_section = True
            continue

        if not education_section:
            continue

        # Stop at other sections
        if re.search(
            r'^(experience|skills|projects|certifications|achievements|internship)',
            line, re.IGNORECASE
        ):
            break

        # Look for degree keywords
        if re.search(
            r'B\.?E|B\.?Tech|Bachelor|B\.?Sc|M\.?Tech|Master|MBA|PhD|'
            r'10th|12th|HSC|SSC|Diploma|Higher Secondary|Secondary',
            line, re.IGNORECASE
        ):
            # Extract CGPA separately
            cgpa_match = re.search(
                r'(?:CGPA|GPA|Score|Percentage)[:\s]*(\d+\.?\d*\s*[/]?\s*\d*\.?\d*\s*%?)',
                line, re.IGNORECASE
            )

            # Extract year separately
            year_match = re.search(r'(20\d{2})', line)

            # Clean degree — remove year and CGPA from it
            degree = line
            degree = re.sub(r'\d{4}\s*[-–?]\s*\d{4}', '', degree)
            degree = re.sub(r'\d{4}', '', degree)
            degree = re.sub(
                r'(?:CGPA|GPA|Score)[:\s]*\d+\.?\d*\s*[/]?\s*\d*\.?\d*',
                '', degree, flags=re.IGNORECASE
            )
            degree = re.sub(r'\s+', ' ', degree).strip()
            degree = degree.strip('|?–-').strip()

            # Get institution from next line
            institution = None
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and len(next_line) > 3:
                    # Clean institution — remove CGPA and scores
                    institution = re.sub(
                        r'(?:CGPA|Score|%)[:\s]*\d+\.?\d*.*',
                        '', next_line, flags=re.IGNORECASE
                    )
                    institution = re.sub(r'\|.*', '', institution)
                    institution = institution.strip()

            education_list.append({
                "degree"     : degree[:200] if degree else None,
                "institution": institution[:200] if institution else None,
                "year"       : year_match.group(1) if year_match else None,
                "cgpa"       : cgpa_match.group(1).strip() if cgpa_match else None
            })

    return education_list

# ─────────────────────────────────────────
# EXTRACT EXPERIENCE
# ─────────────────────────────────────────

def extract_experience(text: str) -> list:
    experience_list = []
    lines = text.split("\n")
    experience_section = False
    current_exp = {}

    for i, line in enumerate(lines):
        if re.search(r'experience|work history|employment', line, re.IGNORECASE):
            experience_section = True
            continue

        if experience_section:
            if re.search(
                r'^(education|skills|projects|certifications|achievements)',
                line, re.IGNORECASE
            ):
                if current_exp:
                    experience_list.append(current_exp)
                break

            date_match = re.search(
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|'
                r'March|April|June|July|August|September|October|November|December)'
                r'\s+\d{4}\s*[-–]\s*(Present|\w+\s+\d{4})',
                line, re.IGNORECASE
            )

            if date_match:
                if current_exp:
                    experience_list.append(current_exp)
                current_exp = {
                    "duration"    : date_match.group(0),
                    "company_name": lines[i - 1].strip() if i > 0 else None,
                    "role"        : lines[i + 1].strip() if i + 1 < len(lines) else None,
                    "description" : ""
                }
            elif current_exp and line.strip():
                current_exp["description"] = (
                    current_exp.get("description", "") + line.strip() + " "
                )

    if current_exp:
        experience_list.append(current_exp)

    return experience_list


# ─────────────────────────────────────────
# EXTRACT TOTAL EXPERIENCE
# ─────────────────────────────────────────

def extract_total_experience(text: str) -> str:
    pattern = r'(\d+\.?\d*)\s*\+?\s*(years?|yrs?)\s*(of)?\s*(experience)?'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(0).strip()

    exp_list = extract_experience(text)
    if exp_list:
        return f"Approx. {len(exp_list)} position(s)"

    return "Fresher"


# ─────────────────────────────────────────
# EXTRACT PROJECTS
# ─────────────────────────────────────────

def extract_projects(text: str) -> list:
    projects = []
    lines = text.split("\n")
    project_section = False

    for line in lines:
        if re.search(r'^projects?', line, re.IGNORECASE):
            project_section = True
            continue

        if project_section:
            if re.search(
                r'^(experience|skills|education|certifications|achievements)',
                line, re.IGNORECASE
            ):
                break
            if line.strip():
                projects.append(line.strip())

    return projects


# ─────────────────────────────────────────
# EXTRACT CERTIFICATIONS
# ─────────────────────────────────────────

def extract_certifications(text: str) -> list:
    certifications = []
    lines = text.split("\n")
    cert_section = False

    for line in lines:
        if re.search(r'certifications?|certificates?|courses?', line, re.IGNORECASE):
            cert_section = True
            continue

        if cert_section:
            if re.search(
                r'^(experience|skills|education|projects|achievements)',
                line, re.IGNORECASE
            ):
                break
            if line.strip():
                certifications.append(line.strip())

    return certifications