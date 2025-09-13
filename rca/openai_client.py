# rca/openai_client.py (secure)
import os, traceback
from typing import Optional
from openai import OpenAI

SYSTEM_PROMPT = """You are a helpful assistant that writes reading passages for primary school students.
Write a single coherent passage that:
- Matches the requested grade level.
- Adjusts difficulty by level: 'Support' = simpler vocabulary/sentences; 'Core' = typical grade level; 'Extension' = slightly more complex vocab/sentences and a subtle inferential layer.
- Uses age-appropriate, factual content.
- Stays within the requested word-length band.
- If keywords or learning outcomes are provided, gently incorporate them.
Write only the passage text; no headings, no bullet points.
"""

def _length_to_bounds(length_label: str):
    if "Short" in length_label: return (120, 180)
    if "Long" in length_label:  return (260, 350)
    return (180, 260)

def generate_passage(grade: str, level: str, length: str,
                     keywords: Optional[str] = "", learning_outcomes: Optional[str] = "") -> str:
    lo, hi = _length_to_bounds(length)
    user_prompt = f"""
Write a reading passage for Grade {grade}.
Level: {level}.
Target length: {lo}-{hi} words.
Keywords: {keywords or "None"}.
Learning outcomes to support: {learning_outcomes or "None"}.
Tone: engaging but age-appropriate. Avoid brand names. Keep it coherent and self-contained.
"""

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return "(Local fallback: no OPENAI_API_KEY set. Set it in your shell or Streamlit Secrets.)"

    try:
        client = OpenAI(api_key=api_key)
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        resp = client.chat.completions.create(
            model=model_name,
            temperature=0.7,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt.strip()}
            ],
            timeout=30
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"(Local fallback due to error)\nError: {e}\n\n{traceback.format_exc()}"
