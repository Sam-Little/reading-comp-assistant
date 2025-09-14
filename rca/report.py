# rca/report.py
from html import escape
from typing import List, Dict, Optional

def build_text_report(passage: str, questions: List[Dict], answers: Dict[str, str], student_name: Optional[str] = "") -> str:
    lines = []
    lines.append("Reading Comprehension – Quiz Report")
    lines.append("=" * 40)
    if student_name:
        lines.append(f"Student: {student_name}")
    lines.append("")
    lines.append("Passage:")
    lines.append(passage.strip())
    lines.append("")
    lines.append("Questions & Answers:")
    correct_count = 0
    for i, q in enumerate(questions, start=1):
        user = answers.get(q["id"], "")
        correct = q["correct_answer"]
        is_correct = (user.strip().lower() == correct.strip().lower()) if q["qtype"] == "wh_mcq" else None
        lines.append(f"{i}. ({q['qtype']}) {q['prompt']}")
        lines.append(f"   - Student: {user or '(no answer)'}")
        lines.append(f"   - Correct: {correct}")
        if is_correct is not None:
            lines.append(f"   - MCQ Correct?: {'Yes' if is_correct else 'No'}")
        lines.append(f"   - Evidence: {q['evidence']}")
        lines.append("")
        if is_correct:
            correct_count += 1
    lines.append(f"Summary: {correct_count} correct (MCQ only), {len(questions)} total questions")
    return "\n".join(lines)

def build_html_report(passage: str, questions: List[Dict], answers: Dict[str, str], student_name: Optional[str] = "") -> str:
    esc = escape
    rows = []
    for i, q in enumerate(questions, start=1):
        user = answers.get(q["id"], "")
        correct = q["correct_answer"]
        rows.append(f"""
        <tr>
          <td style="vertical-align:top;">{i}</td>
          <td>{esc(q['qtype'])}</td>
          <td>{esc(q['prompt'])}</td>
          <td>{esc(user or '(no answer)')}</td>
          <td>{esc(correct)}</td>
          <td>{esc(q['evidence'])}</td>
        </tr>""")
    table = "\n".join(rows)
    student_line = f"<p><strong>Student:</strong> {esc(student_name)}</p>" if student_name else ""
    return f"""
<html>
  <body style="font-family: Arial, sans-serif; color:#111;">
    <h2>Reading Comprehension – Quiz Report</h2>
    {student_line}
    <h3>Passage</h3>
    <p>{esc(passage.strip())}</p>
    <h3>Questions & Answers</h3>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
      <thead>
        <tr style="background:#f4f6f8;">
          <th>#</th><th>Type</th><th>Prompt</th><th>Student</th><th>Correct</th><th>Evidence</th>
        </tr>
      </thead>
      <tbody>
        {table}
      </tbody>
    </table>
  </body>
</html>
"""
