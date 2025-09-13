# app.py (Home)
import streamlit as st

st.set_page_config(page_title="RCA Home", page_icon="📘", layout="wide")

# Load styles
try:
    with open("assets/styles.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

# Top nav bar
st.markdown("""
<div class="topnav">
  <div class="nav-left">
    <a class="brand" href="/">RCA</a>
  </div>
  <div class="nav-right">
    <a class="navlink active" href="/">Home</a>
    <a class="navlink" href="/?page=reading">Reading Comp</a>
    <a class="navlink" href="/?page=create">Create Passage</a>
  </div>
</div>
""", unsafe_allow_html=True)

# Hero / logo circle
st.markdown("""
<div class="hero">
  <div class="logo-circle">RCA</div>
  <h1 class="hero-title">Reading Comprehension Assistant</h1>
  <p class="hero-sub">Generate questions, give instant feedback, and create leveled passages for your class.</p>
  <div class="hero-cta">
    <a class="cta" href="/?page=reading">Start: Reading Comp →</a>
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()
st.subheader("What’s inside?")
st.markdown("""
- **Reading Comp:** paste a passage → auto-generate Cloze & WH/MCQ questions with instant feedback.
- **Create Passage:** generate a leveled passage with grade, support/extension, and optional keywords/learning outcomes.
""")
