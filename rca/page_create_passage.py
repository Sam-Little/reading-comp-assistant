import os
import streamlit as st
from rca.gemini_client import generate_passage
COPY_BUTTON_JS = """
<script>
function copyToClipboard(textId) {
    const textElement = document.getElementById(textId);
    if (!textElement) return;

    // Use a temporary textarea for copying, as st.code is tricky
    const textarea = document.createElement('textarea');
    textarea.value = textElement.innerText;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);

    // Provide visual feedback
    const button = document.getElementById('copy_button_' + textId);
    if (button) {
        button.innerText = 'Copied!';
        setTimeout(() => { 
            button.innerText = 'Copy Passage'; 
            button.style.backgroundColor = '#2c3e50'; 
        }, 1500);
    }
}
</script>
"""
def render_page():
    """Renders the Create Passage tool UI and handles flow to the Quiz Editor."""
    
    st.title("📝 Create a Leveled Passage")

    st.markdown("Provide the **grade**, choose **Support/Core/Extension**, and optional **keywords/learning outcomes** to guide the generator.")

    # --- INPUTS ---
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

    # --- GENERATION LOGIC ---
    if generate:
        with st.spinner("Generating..."):
            st.session_state.gen_result = generate_passage(
                grade=grade,
                level=level,
                length=length,
                keywords=keywords,
                learning_outcomes=los
            )
        
        # Clear the hand-off state in case of failure/old content
        st.session_state.current_passage = ""

    # --- RESULT DISPLAY AND HAND-OFF ---
    if st.session_state.gen_result:
        st.divider()
        st.subheader("Result")
        st.write(st.session_state.gen_result)
        
        # --- NEW BUTTON LOGIC FOR SEAMLESS FLOW ---
        
        # This button triggers the hand-off
        if st.button("Create Quiz & Go to Editor", type="secondary", use_container_width=True):
            # 1. Save the generated text to the common session state variable
            st.session_state.current_passage = st.session_state.gen_result
            
            # 2. Change the view state (app.py router detects this)
            st.session_state.teacher_view = "reading_comp"
            
            # 3. Trigger a refresh to load the new page
            st.rerun() 
            
        st.download_button("Download passage.txt", st.session_state.gen_result, file_name="passage.txt")