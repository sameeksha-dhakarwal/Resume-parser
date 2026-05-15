import pdfplumber
import re

with pdfplumber.open("resume.pdf") as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text() + "\n"

print("\nFULL TEXT:\n", text)

email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+", text)

phone = re.findall(r"\+?\d[\d\s\-]{8,15}", text)

lines = text.split("\n")
name = lines[0] if lines else "Not Found"

print("\n--- Extracted Info ---")
print("Name:", name)
print("Email:", email[0] if email else "Not Found")
print("Phone:", phone[0] if phone else "Not Found")

skills_section = ""

skills_headings = [
    "skills",
    "technical skills",
    "technical expertise",
    "core competencies",
    "technologies",
    "tech stack",
    "key skills"
]


end_headings = [
    "education",
    "experience",
    "work experience",
    "projects",
    "certifications",
    "internships",
    "summary"
]


skills_pattern = r"(" + "|".join(skills_headings) + r")(.*?)(" + "|".join(end_headings) + r"|$)"

match = re.search(skills_pattern, text, re.IGNORECASE | re.DOTALL)

if match:
    skills_section = match.group(2)

print("\nSkills Section:")
print(skills_section.strip())


experience_section = ""

experience_headings = [
    "experience",
    "work experience",
    "professional experience",
    "internship",
    "internships"
]

end_headings = [
    "education",
    "skills",
    "projects",
    "certifications",
    "summary"
]

exp_pattern = r"(" + "|".join(experience_headings) + r")(.*?)(" + "|".join(end_headings) + r"|$)"

exp_match = re.search(exp_pattern, text, re.IGNORECASE | re.DOTALL)

if exp_match:
    experience_section = exp_match.group(2)

print("\nExperience Section:")
print(experience_section.strip())


projects_section = ""

project_headings = [
    "projects",
    "personal projects",
    "academic projects"
]

proj_pattern = r"(" + "|".join(project_headings) + r")(.*?)(" + "|".join(end_headings) + r"|$)"

proj_match = re.search(proj_pattern, text, re.IGNORECASE | re.DOTALL)

if proj_match:
    projects_section = proj_match.group(2)

print("\nProjects Section:")
print(projects_section.strip())