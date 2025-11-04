import streamlit as st

# --- User Database ---
# This is mock data. In a real app, this would be in a secure database.
USER_CREDENTIALS = {
    "teacher_sam": {
        "password": "securepass",
        "role": "Teacher",
        "name": "Sam (Teacher)"
    },
    "student_test1": {
        "password": "securepass",
        "role": "Student",
        "name": "Test Student 1"
    },
    "student_test2": {
        "password": "securepass",
        "role": "Student",
        "name": "Test Student 2"
    }
}

# --- Session State Management ---

def init_session_state():
    """Initializes all required session state variables."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "role" not in st.session_state:
        st.session_state.role = None
    if "auth_error" not in st.session_state:
        st.session_state.auth_error = False
    
    # This tracks which sub-page the teacher is on.
    if "teacher_view" not in st.session_state:
        # --- FIX: ADDED THE MISSING INDENTED BLOCK ---
        st.session_state.teacher_view = "dashboard"

# --- Core Authentication Functions ---

def check_credentials(username, password):
    """
    Checks if the username and password are valid.
    Returns the cleaned username on success, False on failure.
    """
    
    # Strip whitespace to prevent login failures from typos
    clean_username = username.strip() 
    
    if clean_username in USER_CREDENTIALS:
        if USER_CREDENTIALS[clean_username]["password"] == password:
            # --- FIX: Returns the username string, NOT True ---
            return clean_username  
    return False # Return False if any check fails

def logout():
    """Logs the user out and resets session state."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.auth_error = False
    
    # Reset the teacher view on logout
    st.session_state.teacher_view = "dashboard"