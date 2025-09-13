# pages/2_Create_Passage.py
import os
import streamlit as st
from rca.openai_client import generate_passage

st.set_page_config(page_title="Create Passage", page_icon="📝", layout="wide")

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
    <a class="navlink" href="/">Home</a>
    <a class="navlink" href="/?page=reading">Reading Comp</a>
    <a class="navlink active" href="/?page=create">Create Passage</a>
  </div>
</div>
""", unsafe_allow_html=True)

st.title("📝 Create a Leveled Passage")

st.markdown("Provide the **grade**, choose **Support/Core/Extension**, and optional **keywords/learning outcomes** to guide the generator.")

col1, col2 = st.columns(2)
with col1:
    grade = st.selectbox("Grade level", ["1","2","3","4","5","6"], index=0)
    level = st.selectbox("Level", ["Support","Core","Extension"], index=0)
with col2:
    length = st.selectbox("Approx. length", ["Short (120–180 words)","Medium (180–260)","Long (260–350)"], index=0)

keywords = st.text_input("Optional: keywords (comma-separated)", placeholder="e.g., fossils, museum, skeleton")
los = st.text_area("Optional: learning outcomes", placeholder="e.g., Identify main idea; Recognise sequencing words; Use past tense verbs")

generate = st.button("Generate Passage", type="primary")

if "gen_result" not in st.session_state:
    st.session_state.gen_result = ""

if generate:
    with st.spinner("Generating..."):
        st.session_state.gen_result = generate_passage(
            grade=grade,
            level=level,
            length=length,
            keywords=keywords,
            learning_outcomes=los
        )

if st.session_state.gen_result:
    st.divider()
    st.subheader("Result")
    st.write(st.session_state.gen_result)
    st.download_button("Download passage.txt", st.session_state.gen_result, file_name="passage.txt")
