import pdfplumber
import pytesseract
import cv2
import re
import os

from groq_parser import extract_with_groq

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# -----------------------------
# 1. Extract Text
# -----------------------------
def extract_text(file_path):
    ext = file_path.split(".")[-1].lower()
    text = ""

    if ext == "pdf":
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"

    elif ext in ["png", "jpg", "jpeg"]:
        img = cv2.imread(file_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(thresh)

    return text


# -----------------------------
# 2. Contact Info
# -----------------------------
def extract_contact(text):
    email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+", text)
    phone = re.findall(r"\+?\d[\d\s\-]{8,15}", text)

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    name = lines[0] if lines else "Not Found"

    return name, email, phone


# -----------------------------
# 3. Section Extractor
# -----------------------------
def extract_section(text, start_words, end_words):
    pattern = r"(?:^|\n)\s*(" + "|".join(start_words) + r")\s*(.*?)(?=\n\s*(?:" + "|".join(end_words) + r")|\Z)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(2).strip() if match else ""


# -----------------------------
# 4. Skills
# -----------------------------
def extract_skills(text):
    return extract_section(
        text,
        ["skills", "technical skills", "technical expertise"],
        ["experience", "projects", "education", "certifications"]
    )


# -----------------------------
# 5. Experience
# -----------------------------
def extract_experience(text):
    section = extract_section(
        text,
        ["experience", "internships", "work experience"],
        ["projects", "education", "skills"]
    )

    lines = [l.strip() for l in section.split("\n") if l.strip()]
    results = []

    for line in lines:
        match = re.search(r"(.+?)\s*-\s*(.+?)\s*\((.*?)\)", line)

        if match:
            results.append({
                "company": match.group(1),
                "role": match.group(2),
                "duration": match.group(3)
            })

    return results


# -----------------------------
# 6. Projects
# -----------------------------
def extract_projects(text):
    lines = text.split("\n")

    capture = False
    project_lines = []

    for line in lines:
        lower = line.lower()

        if "project" in lower:
            capture = True
            continue

        if capture and any(x in lower for x in ["education", "experience", "skills"]):
            break

        if capture:
            project_lines.append(line.strip())

    results = []
    current_project = None
    tech_stack = set()

    for line in project_lines:

        if line.endswith(":") or len(line.split()) <= 6:
            if current_project:
                results.append({
                    "project": current_project,
                    "tech_stack": list(tech_stack)
                })

            current_project = line.replace(":", "")
            tech_stack = set()
            continue

        tech = re.findall(
            r"(python|java|sql|react|node|tensorflow|nlp|ai|ml)",
            line,
            re.IGNORECASE
        )

        tech_stack.update([t.lower() for t in tech])

    if current_project:
        results.append({
            "project": current_project,
            "tech_stack": list(tech_stack)
        })

    return results


# -----------------------------
# 7. EXTRA SECTIONS (NEW 🔥)
# -----------------------------
def extract_all_sections(text):
    sections = {}

    headings = [
        "education",
        "certifications",
        "achievements",
        "summary",
        "position of responsibilities"
    ]

    for h in headings:
        content = extract_section(
            text,
            [h],
            ["skills", "experience", "projects", "education"]
        )
        if content:
            sections[h] = content

    return sections


# -----------------------------
# 8. MAIN FUNCTION (FINAL 🔥)
# -----------------------------
def parse_resume(file_path):
    file_type = file_path.split(".")[-1].lower()
    file_size = round(os.path.getsize(file_path) / 1024, 2)

    text = extract_text(file_path)

    # fallback parsing
    name, email, phone = extract_contact(text)
    skills = extract_skills(text)
    experience = extract_experience(text)
    projects = extract_projects(text)
    extra_sections = extract_all_sections(text)

    skills_list = [s.strip() for s in skills.split("\n") if s.strip()]

    # AI parsing
    ai_data = extract_with_groq(text)

    # 🔥 FIXED ATS SCORE
    ats_score = 0

    if isinstance(ai_data.get("skills"), list) and len(ai_data["skills"]) > 0:
        ats_score += 30

    if isinstance(ai_data.get("experience"), list) and len(ai_data["experience"]) > 0:
        ats_score += 30

    if isinstance(ai_data.get("projects"), list) and len(ai_data["projects"]) > 0:
        ats_score += 20

    if ai_data.get("email"):
        ats_score += 10

    if ai_data.get("phone"):
        ats_score += 10

    ats_score = min(ats_score, 100)

    return {
        "file_info": {
            "type": file_type,
            "size_kb": file_size
        },
        "ats_score": ats_score,
        "raw_text": text,
        "parsed_data": ai_data,

        "fallback": {
            "contact": {
                "name": name,
                "email": email[0] if email else "",
                "phone": phone[0] if phone else ""
            },
            "skills": skills_list,
            "experience": experience,
            "projects": projects,
            "extra_sections": extra_sections
        }
    }


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    print(parse_resume("Resume.pdf"))