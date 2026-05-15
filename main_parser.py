import pdfplumber
import pytesseract
import cv2
import re
import os

from groq_parser import structure_resume, summarize_experience, summarize_projects, extract_contact_with_links, parse_skills, parse_education

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# -----------------------------
# 1. Extract Text + Hidden Links
# -----------------------------
def extract_text(file_path):
    ext = file_path.split(".")[-1].lower()
    text = ""
    hyperlinks = []

    if ext == "pdf":
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # Extract visible text
                content = page.extract_text()
                if content:
                    text += content + "\n"

                # Extract embedded/hidden hyperlinks
                if hasattr(page, 'hyperlinks') and page.hyperlinks:
                    for link in page.hyperlinks:
                        uri = link.get("uri", "")
                        if uri:
                            hyperlinks.append(uri)

                # Also try annots for older pdfplumber versions
                try:
                    if page.annots:
                        for annot in page.annots:
                            uri = annot.get("uri", "")
                            if uri:
                                hyperlinks.append(uri)
                except Exception:
                    pass

    elif ext in ["png", "jpg", "jpeg"]:
        img = cv2.imread(file_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(thresh)

    # Deduplicate links
    hyperlinks = list(set(hyperlinks))

    return text, hyperlinks


# -----------------------------
# 2. Contact Info (regex fallback)
# -----------------------------
def extract_contact(text):
    email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+", text)
    phone = re.findall(r"\+?\d[\d\s\-]{8,15}", text)

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    name = lines[0] if lines else "Not Found"

    # Regex-based link detection from raw text
    linkedin = re.findall(r"linkedin\.com/in/[\w\-]+", text, re.IGNORECASE)
    github = re.findall(r"github\.com/[\w\-]+", text, re.IGNORECASE)
    leetcode = re.findall(r"leetcode\.com/[\w\-]+", text, re.IGNORECASE)

    return {
        "name": name,
        "email": email[0] if email else "",
        "phone": phone[0] if phone else "",
        "linkedin": linkedin[0] if linkedin else "",
        "github": github[0] if github else "",
        "leetcode": leetcode[0] if leetcode else "",
        "other_links": []
    }


# -----------------------------
# 3. Classify hyperlinks into categories
# -----------------------------
def classify_links(hyperlinks):
    linkedin = ""
    github = ""
    leetcode = ""
    other = []

    for link in hyperlinks:
        lower = link.lower()
        if "linkedin.com" in lower:
            linkedin = link
        elif "github.com" in lower:
            github = link
        elif "leetcode.com" in lower:
            leetcode = link
        else:
            other.append(link)

    return {
        "linkedin": linkedin,
        "github": github,
        "leetcode": leetcode,
        "other_links": other
    }


# -----------------------------
# 4. Section Extractor
# -----------------------------
def extract_section(text, start_words, end_words):
    pattern = r"(?:^|\n)\s*(" + "|".join(start_words) + r")\s*(.*?)(?=\n\s*(?:" + "|".join(end_words) + r")|\Z)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(2).strip() if match else ""


# -----------------------------
# 5. Skills
# -----------------------------
def extract_skills(text):
    return extract_section(
        text,
        ["skills", "technical skills", "technical expertise"],
        [
            "internship experience", "experience", "work experience",
            "professional experience", "internships",
            "projects", "education", "certifications"
        ]
    )


# -----------------------------
# 6. Experience (raw text for Groq)
# -----------------------------
def extract_experience_text(text):
    return extract_section(
        text,
        [
            "internship experience", "internships",
            "work experience", "professional experience",
            "experience"
        ],
        ["projects", "education", "skills", "certifications",
         "responsibilities", "position of responsibilities"]
    )


# -----------------------------
# 7. Projects (raw text for Groq)
# -----------------------------
def extract_projects_text(text):
    return extract_section(
        text,
        ["projects", "personal projects", "academic projects"],
        ["education", "certifications", "skills", "responsibilities", "position of responsibilities"]
    )


# -----------------------------
# 7b. Education (raw text for Groq)
# -----------------------------
def extract_education_text(text):
    return extract_section(
        text,
        ["education", "academic background", "qualifications"],
        ["skills", "experience", "internship experience", "projects",
         "certifications", "responsibilities", "position of responsibilities"]
    )


# -----------------------------
# 8. EXTRA SECTIONS
# -----------------------------
def extract_all_sections(text):
    sections = {}

    headings = [
        "education",
        "certifications",
        "achievements",
        "summary",
        "position of responsibilities",
        "responsibilities"
    ]

    for h in headings:
        content = extract_section(
            text,
            [h],
            ["skills", "experience", "projects", "education", "certifications"]
        )
        if content:
            sections[h] = content

    return sections


# -----------------------------
# 9. MAIN FUNCTION
# -----------------------------
def parse_resume(file_path):
    file_type = file_path.split(".")[-1].lower()
    file_size = round(os.path.getsize(file_path) / 1024, 2)

    # Extract text AND hyperlinks
    text, hyperlinks = extract_text(file_path)

    # Classify embedded hyperlinks
    link_data = classify_links(hyperlinks)

    # Regex fallback contact
    regex_contact = extract_contact(text)

    # Merge link data: prefer embedded hyperlinks over regex-found ones
    merged_contact = {
        "name": regex_contact["name"],
        "email": regex_contact["email"],
        "phone": regex_contact["phone"],
        "linkedin": link_data["linkedin"] or regex_contact["linkedin"],
        "github": link_data["github"] or regex_contact["github"],
        "leetcode": link_data["leetcode"] or regex_contact["leetcode"],
        "other_links": link_data["other_links"]
    }

    # Extract raw section texts
    experience_text = extract_experience_text(text)
    projects_text = extract_projects_text(text)
    education_text = extract_education_text(text)
    skills = extract_skills(text)
    extra_sections = extract_all_sections(text)

    # Groq: structured contact (also extracts hidden links from text patterns)
    ai_contact = extract_contact_with_links(text)

    # Final contact merge: AI > embedded links > regex
    final_contact = {
        "name": ai_contact.get("name") or merged_contact["name"],
        "email": ai_contact.get("email") or merged_contact["email"],
        "phone": ai_contact.get("phone") or merged_contact["phone"],
        "linkedin": link_data["linkedin"] or ai_contact.get("linkedin") or merged_contact["linkedin"],
        "github": link_data["github"] or ai_contact.get("github") or merged_contact["github"],
        "leetcode": link_data["leetcode"] or ai_contact.get("leetcode") or merged_contact["leetcode"],
        "other_links": list(set(link_data["other_links"] + (ai_contact.get("other_links") or [])))
    }

    # Groq: summarize experience and projects
    summarized_experience = summarize_experience(experience_text) if experience_text else []
    summarized_projects = summarize_projects(projects_text) if projects_text else []

    # Groq: structured skills and education
    structured_skills = parse_skills(skills) if skills else []
    structured_education = parse_education(education_text) if education_text else []

    # Full AI structure (for other fields)
    ai_data = structure_resume(text)

    # ATS Score
    ats_score = 0
    if final_contact.get("email"):
        ats_score += 10
    if final_contact.get("phone"):
        ats_score += 10
    if skills:
        ats_score += 30
    if summarized_experience:
        ats_score += 30
    if summarized_projects:
        ats_score += 20
    ats_score = min(ats_score, 100)

    skills_list = [s.strip() for s in skills.split("\n") if s.strip()]

    return {
        "file_info": {
            "type": file_type,
            "size_kb": file_size
        },
        "ats_score": ats_score,
        "raw_text": text,
        "contact": final_contact,
        "skills": skills_list,
        "structured_skills": structured_skills,
        "structured_education": structured_education,
        "experience": summarized_experience,
        "projects": summarized_projects,
        "extra_sections": extra_sections,
        "ai_data": ai_data
    }


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    import json
    result = parse_resume("Resume.pdf")
    print(json.dumps(result, indent=2))