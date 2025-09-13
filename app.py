import json
import streamlit as st
from rca.qg import generate_questions
from rca.grading import grade_mcq, grade_short_answer
from rca.utils import highlight_span

st.set_page_config(page_title="Reading Comprehension Assistant", page_icon="📘", layout="wide")

# Load styles
try:
    with open("assets/styles.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

st.title("📘 Reading Comprehension Assistant (MVP)")
st.caption("Paste a short passage, generate questions, and get instant feedback with evidence.")

with st.expander("How it works"):
    st.markdown(
        """
- **Cloze** questions remove a key word from a sentence.
- **WH/MCQ** questions hide a named entity (Who/Where/When/Org).
- For each answer, you’ll get **✓/✗** and we’ll show the **evidence sentence**.

> Tip: Keep passages under ~400 words for best results.
"""
    )

col_left, col_right = st.columns([2, 1])

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

with col_left:
    st.subheader("✍️ Passage")
    text = st.text_area("Paste your passage here", value=default_text, height=220,
                        placeholder="Paste or type a short passage (100–400 words)...")
    n_questions = st.slider("Number of questions", 4, 12, 6, step=1)

if "questions" not in st.session_state:
    st.session_state.questions = []
    st.session_state.answers = {}

if st.button("Generate Questions", type="primary", disabled=not text.strip()):
    st.session_state.questions = generate_questions(text, n=n_questions)
    st.session_state.answers = {q["id"]: "" for q in st.session_state.questions}

if st.session_state.questions:
    st.divider()
    st.header("📝 Quiz")
    for q in st.session_state.questions:
        st.subheader(f"Q{q['id'][1:]} — {q['qtype'].upper()}")
        st.write(q["prompt"])
        key = f"ans_{q['id']}"
        if q["qtype"] == "wh_mcq" and q.get("options"):
            user = st.radio("Choose one:", q["options"], key=key, index=None, horizontal=False)
        else:
            user = st.text_input("Your answer:", key=key, placeholder="Type your answer...")

        cols = st.columns([1, 4])
        with cols[0]:
            if st.button("Check", key=f"check_{q['id']}"):
                st.session_state.answers[q["id"]] = user or ""

        user_saved = st.session_state.answers.get(q["id"], "")
        if user_saved:
            if q["qtype"] == "wh_mcq":
                result = grade_mcq(user_saved, q["correct_answer"])
            else:
                result = grade_short_answer(user_saved, q["correct_answer"])

            if result["is_correct"]:
                st.markdown("<div class='feedback-correct'>✅ Correct!</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='feedback-wrong'>❌ Not quite.</div>", unsafe_allow_html=True)

            evidence_html = highlight_span(q["evidence"], q["correct_answer"])
            st.markdown(f"""
**Evidence:**  
<div class='evidence'>{evidence_html}</div>
""", unsafe_allow_html=True)
            st.caption(f"Correct answer: **{q['correct_answer']}**")

    st.divider()
    if st.button("Grade All"):
        correct = 0
        total = len(st.session_state.questions)
        for q in st.session_state.questions:
            user = st.session_state.answers.get(q["id"], "")
            if not user:
                continue
            if q["qtype"] == "wh_mcq":
                res = grade_mcq(user, q["correct_answer"])
            else:
                res = grade_short_answer(user, q["correct_answer"])
            if res["is_correct"]:
                correct += 1
        st.success(f"Score: {correct} / {total}")
