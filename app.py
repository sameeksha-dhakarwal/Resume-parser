from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re

from main_parser import extract_text, parse_resume, extract_section

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Legacy section splitter (kept for backward compatibility)
def split_sections(text):
    sections = {}
    current_section = "GENERAL"

    lines = text.split("\n")

    for line in lines:
        clean = line.strip()

        if not clean:
            continue

        # detect headings
        if clean.isupper() or clean.lower() in [
            "skills", "projects", "experience", "education",
            "certifications", "internships", "work experience",
            "responsibilities", "position of responsibilities"
        ]:
            current_section = clean.upper()
            sections[current_section] = []
        else:
            sections.setdefault(current_section, []).append(clean)

    return sections


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # file info
    file_type = file.filename.split(".")[-1]
    file_size = round(os.path.getsize(file_path) / 1024, 2)

    # Full parse with Groq AI summaries
    parsed = parse_resume(file_path)

    # Also do raw section split for fallback display
    text = parsed.get("raw_text", "")
    sections = split_sections(text)

    # Extract certifications and responsibilities directly as plain text
    certifications_text = extract_section(
        text,
        ["certifications", "certifications and achievements", "achievements"],
        ["responsibilities", "position of responsibilities", "education",
         "skills", "experience", "projects"]
    )

    responsibilities_text = extract_section(
        text,
        ["responsibilities", "position of responsibilities"],
        ["certifications", "education", "skills", "experience", "projects"]
    )

    # Convert to bullet-point-friendly line lists
    def text_to_lines(t):
        return [l.strip() for l in t.split("\n") if l.strip()] if t else []

    return jsonify({
        "file_info": {
            "type": file_type,
            "size": file_size
        },
        # New structured fields
        "contact": parsed.get("contact", {}),
        "skills": parsed.get("skills", []),
        "structured_skills": parsed.get("structured_skills", []),
        "structured_education": parsed.get("structured_education", []),
        "experience": parsed.get("experience", []),
        "projects": parsed.get("projects", []),
        "certifications": text_to_lines(certifications_text),
        "responsibilities": text_to_lines(responsibilities_text),
        "extra_sections": parsed.get("extra_sections", {}),
        "ai_data": parsed.get("ai_data", {}),
        "ats_score": parsed.get("ats_score", 0),
        # Legacy fallback
        "sections": sections,
        "raw_text": text
    })


if __name__ == "__main__":
    app.run(debug=True)