import json
import streamlit as st
from rca.qg import generate_questions
from rca.grading import grade_mcq, grade_short_answer
from rca.utils import highlight_span
from rca.emailer import send_email
from rca.report import build_text_report, build_html_report

def render_page():
    """Renders the Reading Comprehension tool UI."""

    st.title("🧠 Reading Comprehension")
    st.caption("Paste a passage, generate questions, and get instant feedback.")

    col_left, col_right = st.columns([2, 1])

    # --- Sample Passage Loader ---
    with col_right:
        st.subheader("📚 Samples")
        try:
            with open("data/sample_passages.json", "r", encoding="utf-8") as f:
                samples = json.load(f)
        except Exception:
            samples = []
        sample_titles = ["(none)"] + [s["title"] for s in samples]
        pick = st.selectbox("Load a sample passage:", sample_titles, index=0)
        default_text = ""
        if pick != "(none)":
            chosen = next(s for s in samples if s["title"] == pick)
            default_text = chosen["text"]

    # --- Passage Input ---
    with col_left:
        st.subheader("✍️ Passage")
        text = st.text_area("Paste your passage here", value=default_text, height=220,
                            placeholder="Paste or type a short passage (100–400 words)...")
        n_questions = st.slider("Number of questions", 4, 12, 6, step=1)

    if "questions" not in st.session_state:
        st.session_state.questions = []
        st.session_state.answers = {}
        if "final_score" in st.session_state:
            del st.session_state.final_score

    # --- Question Generation Button ---
    if st.button("Generate Questions", type="primary", disabled=not text.strip()):
        with st.spinner("Generating questions..."):
            st.session_state.questions = generate_questions(text, n=n_questions)
            st.session_state.answers = {q["id"]: "" for q in st.session_state.questions}
            if "final_score" in st.session_state:
                del st.session_state.final_score # Clear old score

    # --- Quiz Display Area ---
    if st.session_state.questions:
        st.divider()
        st.header("📝 Quiz")
        
        # Use a single form for the whole quiz for a cleaner UX
        with st.form(key="quiz_form"):
            for q in st.session_state.questions:
                st.subheader(f"Q{q['id'][1:]} — {q['qtype'].upper()}")
                st.write(q["prompt"])
                key = f"ans_{q['id']}"
                
                if q["qtype"] == "wh_mcq" and q.get("options"):
                    st.radio("Choose one:", q["options"], key=key, index=None, horizontal=False)
                else:
                    st.text_input("Your answer:", key=key, placeholder="Type your answer...")

            quiz_submitted = st.form_submit_button("Check All Answers & Get Feedback")

        # --- Results Display Area (Shows after form is submitted) ---
        if quiz_submitted:
            st.divider()
            st.header("🔍 Results & Feedback")
            
            correct = 0
            total = len(st.session_state.questions)
            
            # Store answers from form submit
            for q in st.session_state.questions:
                 st.session_state.answers[q["id"]] = st.session_state[f"ans_{q['id']}"]

            # Grade and display results
            for q in st.session_state.questions:
                st.subheader(f"Q{q['id'][1:]} Feedback")
                user_saved = st.session_state.answers.get(q["id"], "")

                if not user_saved:
                    st.warning("No answer provided.")
                    st.markdown("---")
                    continue

                if q["qtype"] == "wh_mcq":
                    result = grade_mcq(user_saved, q["correct_answer"])
                else:
                    result = grade_short_answer(user_saved, q["correct_answer"])

                if result["is_correct"]:
                    correct += 1
                    st.markdown("<div class='feedback-correct'>✅ Correct!</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='feedback-wrong'>❌ Not quite.</div>", unsafe_allow_html=True)
                
                st.write(f"Your answer: *{user_saved}*")
                st.caption(f"Correct answer: **{q['correct_answer']}**")
                
                try:
                    evidence_html = highlight_span(q["evidence"], q["correct_answer"])
                    st.markdown(f"**Evidence:**\n<div class='evidence'>{evidence_html}</div>", unsafe_allow_html=True)
                except Exception:
                    st.markdown(f"**Evidence:**\n<div class='evidence'>{q['evidence']}</div>", unsafe_allow_html=True)
                
                st.markdown("---")
            
            st.header(f"Final Score: {correct} / {total}")
            st.session_state.final_score = f"{correct} / {total}" # Store score for email


        # --- Email Reporting Section (Shows after results are calculated) ---
        if "final_score" in st.session_state:
            st.divider()
            st.subheader("📧 Send Results to Teacher")
            
            with st.form(key="email_form"):
                colA, colB = st.columns([1, 1])
                with colA:
                    student_name = st.text_input("Student name (optional)", placeholder="e.g., Alex Kim")
                with colB:
                    teacher_email = st.text_input("Teacher's email", placeholder="teacher@example.com")
                
                email_submitted = st.form_submit_button("Send Report", type="primary")

                if email_submitted:
                    if not teacher_email or "@" not in teacher_email:
                        st.error("Please enter a valid teacher email.")
                    else:
                        passage_text = text or ""
                        text_report = build_text_report(passage_text, st.session_state.questions, st.session_state.answers, student_name=student_name)
                        html_report = build_html_report(passage_text, st.session_state.questions, st.session_state.answers, student_name=student_name)

                        subject = "Reading Comprehension – Quiz Report"
                        if student_name:
                            subject += f" ({student_name})"

                        with st.spinner("Sending email..."):
                            status = send_email(
                                to_email=teacher_email,
                                subject=subject,
                                body_text=text_report,
                                body_html=html_report
                            )

                        if status == "OK":
                            st.success(f"Sent to {teacher_email}")
                        else:
                            st.error(status)
                            st.info("Tip: Set SMTP_USER and SMTP_PASS (App Password) in your environment.")

