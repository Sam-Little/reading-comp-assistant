import streamlit as st

# --- Mock User Database ---
# This dictionary acts as the temporary user database for the MVP.
USER_CREDENTIALS = {
    "teacher_sam": {"password": "sam_pass", "role": "Teacher"},
    "teacher_filip": {"password": "filip_pass", "role": "Teacher"},
    "student_test1": {"password": "student1", "role": "Student"},
    "student_test2": {"password": "student2", "role": "Student"}
}

# --- Session State Initialization ---
def init_session_state():
    """Initializes session state variables if they don't exist."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'auth_error' not in st.session_state:
        st.session_state.auth_error = False

# --- Core Authentication Logic ---
def check_credentials(username, password):
    """Checks the provided credentials against the mock database."""
    if username in USER_CREDENTIALS:
        user_data = USER_CREDENTIALS[username]
        if password == user_data["password"]:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user_data["role"]
            st.session_state.auth_error = False
            return True
    st.session_state.auth_error = True
    return False

def logout():
    """Resets the session state for logout."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.auth_error = False

def login_form():
    """Displays the login form."""
    if st.session_state.auth_error:
         st.session_state.auth_error = False

    with st.form("login_form"):
        st.subheader("RCA Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")

        if submitted:
            if check_credentials(username, password):
                st.success(f"Welcome, {st.session_state.role}!")
                st.experimental_rerun()
            else:
                st.session_state.auth_error = True
                st.experimental_rerun()
