import os
import streamlit as st
from rca.gemini_client import generate_passage

def render_page():
    """Renders the Create Passage tool UI."""
    
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

