import streamlit as st
# Import the auth logic needed for the form
# We now get USER_CREDENTIALS to look up the role after validation
from rca.auth import check_credentials, USER_CREDENTIALS 

def render_home_page():
    """
    Renders the main login invitation page.
    This page is shown *only* to users who are NOT logged in.
    It contains the functional, centralized login form.
    """
    
    # --- Load CSS ---
    try:
        with open("assets/styles.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass # Handle case where CSS file is not found

    # --- Hero / Logo and Title ---
    st.markdown("""
        <div class="hero" style="text-align: center; margin-top: 50px;">
            <div class="logo-circle" style="margin-bottom: 20px;">RCA</div>
            <h1 class="hero-title">Reading Comprehension Assistant</h1>
            <p class="hero-sub">A tool for efficient, data-driven formative assessment.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Centralized Login Form ---
    # Create columns to center the login form
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.subheader("Login to Your Dashboard")
        st.markdown("Please use the credentials provided for your role (Teacher or Student).")

        with st.form("login_form_main", clear_on_submit=False):
            username = st.text_input(
                "Username", 
                placeholder="e.g., teacher_sam"
            )
            password = st.text_input(
                "Password", 
                type="password",
                placeholder="e.g., securepass"
            )
            
            # Form submission button
            submitted = st.form_submit_button("Log In", use_container_width=True)

            if submitted:
                # --- THIS IS THE CRITICAL FIX ---
                # Call check_credentials and store the return value
                valid_username = check_credentials(username, password) # This will be "teacher_sam" or False
                
                # Check if the return value is a username (string) or False
                if valid_username:
                    # Set session state variables using the CLEANED username
                    st.session_state.logged_in = True
                    st.session_state.username = valid_username 
                    st.session_state.role = USER_CREDENTIALS[valid_username]["role"]
                    st.session_state.auth_error = False
                    
                    # Trigger an immediate rerun.
                    # app.py will detect the new 'logged_in' state and show the correct dashboard.
                    st.rerun() 
                else:
                    # Login failed
                    st.session_state.logged_in = False
                    st.session_state.auth_error = True


        # Display login error message if authentication failed
        if st.session_state.get("auth_error", False):
            st.error("Invalid username or password. Please try again.")

    st.markdown("---")

    # --- Footer / Feature Description ---
    st.markdown("""
        <div style="text-align: center; margin-top: 30px;">
            <h4>What’s inside?</h4>
            <p>
                - <strong>For Teachers:</strong> Generate leveled passages, create quizzes, and analyze student data.<br/>
                - <strong>For Students:</strong> Take assigned quizzes and get instant, evidence-based feedback.
            </p>
        </div>
    """, unsafe_allow_html=True)

