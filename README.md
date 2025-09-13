# Reading Comprehension Assistant (MVP)

Streamlit app that turns a short passage into 4–12 comprehension questions (Cloze + WH/MCQ), lets students answer, and gives instant feedback with an evidence sentence highlight.

## Quick Start
1) Create and activate a virtual environment.
2) `pip install -r requirements.txt`
3) `python -m spacy download en_core_web_sm`
4) Python one-liner to download NLTK data:
   ```python
   import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')
