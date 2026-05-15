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
