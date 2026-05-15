# ResumeIQ Parser 📄

AI-powered resume parser with a **3-layer fallback engine**, intelligent structured extraction, and a modern **React + Vite frontend** connected to a Python backend.

---

## Color Palette

| Name | Hex |
|------|------|
| Gochujang Red | `#780000` |
| Crimson Blaze | `#C1121F` |
| Varden | `#FFF8E1` |
| Cosmos Blue | `#003049` |
| Blue Marble | `#669BBC` |

---

# How It Works — 3-Layer Parsing Engine

Every uploaded resume passes through a multi-layer parsing pipeline.  
If one layer fails, the system automatically falls back to the next one.

```text
Resume File
    ↓
Text Extraction
    ├── .txt  → Plain decode
    ├── .pdf  → pdfplumber → fallback to PaddleOCR
    ├── .docx → python-docx
    └── .doc  → antiword → fallback python-docx
    ↓
Raw Text
    ↓
┌─────────────────────────────────┐
│  Layer 1 · Groq LLaMA 3.3 70B  │  ← primary AI parser
└──────────────┬──────────────────┘
               │ fails?
┌──────────────▼──────────────────┐
│  Layer 2 · Rule-Based Parsing   │  ← offline fallback
└──────────────┬──────────────────┘
               │ fails?
┌──────────────▼──────────────────┐
│  Layer 3 · Regex Extraction     │  ← always works
└─────────────────────────────────┘
    ↓
Structured JSON
    {name, email, phone, skills, experience, education, certifications}
    ↓
Frontend Display
    → preview parsed data → export JSON

---

## Supported Formats

| Format | Method | Notes |
|--------|--------|-------|
| PDF (text) | pdfplumber | Fast and accurate |
| PDF (scanned) | PaddleOCR | OCR fallback |
| DOCX | python-docx | Full text extraction |
| DOC (legacy) | antiword | Windows support required |
| TXT | Plain decode | UTF-8 / Latin-1 |

---

# Project Structure

```text
sameeksha-dhakarwal/
├── app.py                     # Flask backend
├── groq_parser.py             # AI parsing engine
├── extractor.py               # Resume text extraction
├── requirements.txt
├── uploads/                   # Uploaded resumes
├── parsed_output/             # Generated JSON outputs
├── resume-ui/                 # React + Vite frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

# Quick Start

## 1. Open Project Directory

```bash
cd "Sarmak-RecruitIQ\sameeksha-dhakarwal"
```

---

# Backend Setup

## Terminal 1

Inside `sameeksha-dhakarwal`

```bash
python app.py
```

Backend starts on:

```text
http://127.0.0.1:5000
```

---

# Frontend Setup

## Terminal 2

```bash
cd resume-ui
npm install
npm run dev
```

Frontend starts on:

```text
http://localhost:5173
```

---

# API Key Setup

Create a `.env` file or directly configure your Groq API key.

Example:

```python
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
```

Or:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

# Get Free Groq API Key

1. Visit: https://console.groq.com
2. Create an account
3. Open **API Keys**
4. Generate a new key
5. Paste it into your `.env` file

---

# Requirements

## Python Dependencies

```text
Flask
flask-cors
groq
pdfplumber
python-docx
paddleocr
paddlepaddle
PyMuPDF
Pillow
numpy
python-dotenv
```

Install:

```bash
pip install -r requirements.txt
```

---

# Frontend Dependencies

Install frontend packages:

```bash
npm install
```

---

# Notes

- PaddleOCR downloads OCR models during first scanned-PDF parsing
- `.doc` support on Windows requires antiword installed and added to PATH
- Backend and frontend run separately
- The parser automatically falls back if AI extraction fails
- Extracted data is returned as structured JSON

---

# Tech Stack

## Backend

- Python
- Flask
- Groq API
- PaddleOCR
- pdfplumber

## Frontend

- React
- Vite
- JavaScript
- CSS

---

# Future Improvements

- Authentication system
- Resume ranking
- ATS score generation
- Skill matching engine
- Multi-resume batch processing
- Database integration

---

*Built with Groq · Flask · React · Vite · PaddleOCR*
