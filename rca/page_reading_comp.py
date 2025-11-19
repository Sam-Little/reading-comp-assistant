import json
import streamlit as st
from rca.qg import generate_questions


def render_page():
    """Renders the Reading Comprehension Quiz Editor (teacher view)."""

    st.title("🧠 Reading Comprehension – Quiz Editor")
    st.caption("Start from a passage, generate questions, edit them, and export.")

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

        # 1️⃣ Prefer passage from Create Passage page if present
        current_passage = st.session_state.get("current_passage", "")

        # Default text starts as whatever we have from session
        default_text = current_passage

        # 2️⃣ If a sample is selected, override the default with that sample
        if pick != "(none)":
            chosen = next(s for s in samples if s["title"] == pick)
            default_text = chosen["text"]
            # Keep in session for consistency
            st.session_state.current_passage = default_text

        text = st.text_area(
            "Paste your passage here",
            value=default_text,
            height=220,
            placeholder="Paste or type a short passage (100–400 words)...",
        )
        n_questions = st.slider("Number of questions", 4, 12, 6, step=1)

    # We treat this page as teacher-only authoring, so no student answers here
    if "questions" not in st.session_state:
        st.session_state.questions = []

    # --- Question Generation Button ---
    if st.button("Generate Questions", type="primary", disabled=not text.strip()):
        with st.spinner("Generating questions..."):
            st.session_state.questions = generate_questions(text, n_questions)

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
            # You could render a read-only student view here if needed.
        else:
            for i, q in enumerate(st.session_state.questions):
                st.markdown(f"### Q{i+1} — {q.get('qtype', '').upper()}")

                # --- Editable prompt ---
                prompt_key = f"prompt_{q['id']}"
                new_prompt = st.text_area(
                    "Question text",
                    value=q["prompt"],
                    key=prompt_key,
                )
                q["prompt"] = new_prompt  # update in session_state

                # --- MCQ options (if applicable) ---
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
                        current_idx = new_options.index(q["correct_answer"])
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
                    # Short-answer / open-ended: allow editing correct answer text
                    correct_key = f"correct_{q['id']}"
                    new_correct = st.text_input(
                        "Correct answer (for teacher reference)",
                        value=q.get("correct_answer", ""),
                        key=correct_key,
                    )
                    q["correct_answer"] = new_correct

                # Optional: show evidence as read-only if present
                evidence = q.get("evidence")
                if evidence:
                    with st.expander("Show evidence (from passage)"):
                        st.write(evidence)

                st.markdown("---")

        # --- Export / Download section (Teacher side) ---
        if is_teacher:
            st.subheader("⬇️ Export Quiz")

            # Use the latest text from the text area
            final_passage = text

            # Build a simple .txt export
            export_text = "PASSAGE:\n\n"
            export_text += final_passage.strip() + "\n\n"
            export_text += "QUESTIONS:\n\n"

            for i, q in enumerate(st.session_state.questions):
                export_text += f"{i+1}. {q['prompt'].strip()}\n"
                if q.get("qtype") == "wh_mcq" and q.get("options"):
                    for j, opt in enumerate(q["options"]):
                        export_text += f"   {chr(65+j)}. {opt}\n"
                    export_text += f"   [Correct: {q.get('correct_answer', '')}]\n"
                else:
                    export_text += f"   [Expected answer: {q.get('correct_answer', '')}]\n"
                export_text += "\n"

            st.download_button(
                label="Download Quiz (.txt)",
                data=export_text,
                file_name="reading_quiz.txt",
                mime="text/plain",
                use_container_width=True,
            )
