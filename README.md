# Reading Comprehension Assistant (MVP)

Streamlit app that turns a short passage into 4–12 comprehension questions (Cloze + WH/MCQ), lets students answer, and gives instant feedback with an evidence sentence highlight.

## Quick Start

1. **Create and activate a virtual environment**
   ```powershell
   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate

   pip install -r requirements.txt

   python -m spacy download en_core_web_sm

   python -m spacy download en_core_web_sm

    streamlit run app.py