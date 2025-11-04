import streamlit as st
import os

# --- Import Authentication and Page Logic ---
from rca.auth import init_session_state, logout 

# --- IMPORT YOUR REFJACTORED PAGE MODULES ---
# Note the new import paths based on our refactor
from rca.page_home import render_home_page # This is your login screen
from rca import page_create_passage
from rca import page_reading_comp
# --- (You will also need your other modules like rca.gemini_client etc.) ---


# =============================================================================
# --- 1. TEACHER "HUB" and "SPOKE" ROUTER ---
# =============================================================================

def render_teacher_dashboard():
    """
    This is the main "Hub" page for the teacher, with buttons to the tools.
    """
    st.subheader("Teacher Dashboard")
    st.markdown("Welcome to your dashboard. Please select a tool to begin.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🖊️ Create Passage")
        st.markdown("Generate a new, leveled reading passage and quiz from a topic.")
        if st.button("Go to Create Passage", key="nav_create", type="primary"):
            st.session_state.teacher_view = "create_passage"
            st.rerun() # Rerun to load the new view

    with col2:
        st.markdown("#### 📈 Reading Comprehension")
        st.markdown("Paste existing text to generate a quiz or review student analytics.")
        if st.button("Go to Reading Comp", key="nav_read", type="primary"):
            st.session_state.teacher_view = "reading_comp"
            st.rerun() # Rerun to load the new view

def teacher_page():
    """
    This function is now a ROUTER for the teacher's experience.
    It shows the main hub or one of the sub-pages.
    """
    st.title("📚 Teacher Dashboard")
    st.info(f"Welcome, **{st.session_state.username}**.")
    
    # --- Navigation Logic ---
    # Show a "Back to Dashboard" button if we are *not* on the dashboard
    if st.session_state.teacher_view != "dashboard":
        if st.button("← Back to Dashboard", key="back_dash"):
            st.session_state.teacher_view = "dashboard"
            st.rerun()
    
    if st.button("Log Out", key="teacher_logout"):
        logout() 
        st.rerun() 

    st.markdown("---")

    # --- Content Router ---
    # This checks the session state and calls the correct render function
    if st.session_state.teacher_view == "dashboard":
        render_teacher_dashboard()
    elif st.session_state.teacher_view == "create_passage":
        # Calls the function from your refactored file
        page_create_passage.render_page() 
    elif st.session_state.teacher_view == "reading_comp":
        # Calls the function from your refactored file
        page_reading_comp.render_page() 
    else:
        # Fallback in case of an error
        st.session_state.teacher_view = "dashboard"
        st.rerun()

# =============================================================================
# --- 2. STUDENT PAGE ROUTER (Unchanged) ---
# =============================================================================

def student_page():
    """Content for the Student role: Quiz Taking UI."""
    st.title("📝 Student: Reading Comprehension Quiz")
    st.info(f"Welcome, **{st.session_state.username}**. Please complete your assigned task.")
    
    if st.button("Log Out", key="student_logout"): 
        logout() 
        st.rerun() 
        
    st.markdown("---")
    st.subheader("Assigned Quiz: The Solar System")
    st.markdown("*(Passage and quiz questions displayed here.)*")
    
    if st.button("Submit Quiz and Get Instant Feedback"):
        st.balloons()
        st.success("Quiz submitted! Your score has been logged.")
        st.code("Grading logic (fuzzy match) and log_quiz_result() call runs here...")

# =============================================================================
# --- 3. MAIN APPLICATION ROUTER (Final Version) ---
# =============================================================================

def main():
    st.set_page_config(
        page_title="RCA", 
        layout="wide", 
        initial_sidebar_state="collapsed" 
    )

    st.markdown(
        """
        <style>
            div[data-testid="stSidebarNav"] { display: none; }
            button[data-testid="stSidebarNavOpenButton"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    init_session_state()

    if st.session_state.logged_in:
        if st.session_state.role == "Teacher":
            teacher_page()
        elif st.session_state.role == "Student":
            student_page()
    else:
        # This is your functional login screen from rca/page_home.py
        render_home_page() 
        
if __name__ == "__main__":
    main()