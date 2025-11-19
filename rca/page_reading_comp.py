import json
import io
import streamlit as st

from rca.qg import generate_questions

# PDF generation imports
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

def build_quiz_pdf(passage: str, questions: list) -> io.BytesIO:
    """
    Build a student-facing PDF:
    - Includes passage
    - Includes questions
    - NO answers
    - Shows lines/space for students to write
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("<b>Reading Comprehension Quiz</b>", styles["Title"]))
    story.append(Spacer(1, 0.3 * inch))

    # Passage
    story.append(Paragraph("<b>Passage</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(passage.replace("\n", "<br/>"), styles["Normal"]))
    story.append(Spacer(1, 0.4 * inch))

    # Questions
    story.append(Paragraph("<b>Questions</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    for i, q in enumerate(questions):
        prompt = q.get("prompt", "").strip()

        story.append(Paragraph(f"{i + 1}. {prompt}", styles["Normal"]))
        story.append(Spacer(1, 0.1 * inch))

        # MCQ options (no answers revealed)
        if q.get("qtype") == "wh_mcq" and q.get("options"):
            for j, opt in enumerate(q["options"]):
                story.append(Paragraph(f"{chr(65 + j)}. {opt}", styles["Normal"]))
            story.append(Spacer(1, 0.15 * inch))

        # "Lines" for students to write on (3 fake lines)
        for _ in range(3):
            story.append(Paragraph("_" * 100, styles["Normal"]))
            story.append(Spacer(1, 0.05 * inch))

        story.append(Spacer(1, 0.15 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer


def build_answer_key_pdf(passage: str, questions: list) -> io.BytesIO:
    """
    Build a teacher-facing Answer Key PDF:
    - Lists questions and correct answers
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("<b>Reading Comprehension – Answer Key</b>", styles["Title"]))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("<b>Questions & Answers</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    for i, q in enumerate(questions):
        prompt = q.get("prompt", "").strip()
        correct_answer = q.get("correct_answer", "").strip()

        story.append(Paragraph(f"{i + 1}. {prompt}", styles["Normal"]))
        story.append(Spacer(1, 0.05 * inch))

        # Show options for MCQ
        if q.get("qtype") == "wh_mcq" and q.get("options"):
            for j, opt in enumerate(q["options"]):
                story.append(Paragraph(f"{chr(65 + j)}. {opt}", styles["Normal"]))
            story.append(Spacer(1, 0.05 * inch))

        # Show correct answer
        story.append(
            Paragraph(
                f"<b>Answer:</b> {correct_answer if correct_answer else '(not set)'}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer

def render_page():
    """Renders the Reading Comprehension Quiz Editor (teacher view)."""

    st.title("🧠 Reading Comprehension – Quiz Editor")
    st.caption("Start from a passage, generate questions, edit them, and export as PDFs.")

    col_left, col_right = st.columns([2, 1])

    # --- Sample Passage Loader (right) ---
    with col_right:
        st.subheader("📚 Samples")
        try:
            with open("data/sample_passages.json", "r", encoding="utf-8") as f:
                samples = json.load(f)
        except Exception:
            samples = []

        sample_titles = ["(none)"] + [s["title"] for s in samples]
        pick = st.selectbox("Load a sample passage:", sample_titles, index=0)

    # --- Passage Input (left) ---
    with col_left:
        st.subheader("✍️ Passage")

        # Prefer passage from Create Passage page if present
        current_passage = st.session_state.get("current_passage", "")

        default_text = current_passage

        # If a sample is selected, override the default
        if pick != "(none)":
            chosen = next(s for s in samples if s["title"] == pick)
            default_text = chosen["text"]
            st.session_state.current_passage = default_text

        text = st.text_area(
            "Paste your passage here",
            value=default_text,
            height=220,
            placeholder="Paste or type a short passage (100–400 words)...",
        )
        n_questions = st.slider("Number of questions", 4, 12, 6, step=1)

    # Treat this page as teacher-only quiz authoring
    if "questions" not in st.session_state:
        st.session_state.questions = []

    # --- Question Generation Button ---
    if st.button("Generate Questions", type="primary", disabled=not text.strip()):
        with st.spinner("Generating questions..."):
            st.session_state.questions = generate_questions(text, n=n_questions)

        # keep the latest passage in session_state so it's exported correctly
        st.session_state.current_passage = text

    # --- Quiz Editor Area (Teacher view only) ---
    if st.session_state.questions:
        st.divider()
        st.header("📝 Quiz (Teacher Editable)")

        # Simple flag in case you later add a student view
        is_teacher = st.session_state.get("is_teacher", True)

        if not is_teacher:
            st.info("This page is currently in teacher-only mode. Editing is disabled.")
        else:
            for i, q in enumerate(st.session_state.questions):
                st.markdown(f"### Q{i+1} — {q.get('qtype', '').upper()}")

                # Editable prompt
                prompt_key = f"prompt_{q['id']}"
                new_prompt = st.text_area(
                    "Question text",
                    value=q["prompt"],
                    key=prompt_key,
                )
                q["prompt"] = new_prompt

                # MCQ options (if applicable)
                if q.get("qtype") == "wh_mcq" and q.get("options"):
                    st.markdown("**Options**")
                    new_options = []
                    for j, opt in enumerate(q["options"]):
                        opt_key = f"opt_{q['id']}_{j}"
                        new_opt = st.text_input(
                            f"Option {j+1}",
                            value=opt,
                            key=opt_key,
                        )
                        new_options.append(new_opt)

                    # Update options
                    q["options"] = new_options

                    # Choose correct answer from options
                    st.markdown("**Correct option**")
                    try:
                        current_idx = new_options.index(q.get("correct_answer", ""))
                    except ValueError:
                        current_idx = 0 if new_options else 0

                    if new_options:
                        correct_opt = st.selectbox(
                            "Select correct option",
                            new_options,
                            index=current_idx,
                            key=f"correct_{q['id']}",
                        )
                        q["correct_answer"] = correct_opt

                else:
                    # Short-answer / open-ended: editable correct answer text
                    correct_key = f"correct_{q['id']}"
                    new_correct = st.text_input(
                        "Correct answer (for teacher reference)",
                        value=q.get("correct_answer", ""),
                        key=correct_key,
                    )
                    q["correct_answer"] = new_correct

                # Optional: show evidence as read-only
                evidence = q.get("evidence")
                if evidence:
                    with st.expander("Show evidence (from passage)"):
                        st.write(evidence)

                st.markdown("---")

        # --- Export / Download section ---
        if is_teacher:
            st.subheader("⬇️ Export Quiz")

            quiz_pdf = build_quiz_pdf(text, st.session_state.questions)
            answer_key_pdf = build_answer_key_pdf(text, st.session_state.questions)

            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button(
                    label="Download Quiz (PDF)",
                    data=quiz_pdf,
                    file_name="reading_quiz.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            with col_b:
                st.download_button(
                    label="Download Answer Key (PDF)",
                    data=answer_key_pdf,
                    file_name="reading_quiz_answer_key.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
