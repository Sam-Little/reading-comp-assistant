# rca/openai_client.py
import os
from typing import Optional
try:
    # OpenAI Python SDK v1+
    from openai import OpenAI
except Exception:
    OpenAI = None  # handle missing lib gracefully

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
    if "Short" in length_label:
        return (120, 180)
    if "Long" in length_label:
        return (260, 350)
    return (180, 260)

def generate_passage(grade: str, level: str, length: str,
                     keywords: Optional[str] = "", learning_outcomes: Optional[str] = "") -> str:
    """Calls OpenAI if OPENAI_API_KEY is set; otherwise returns a deterministic fallback."""
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
    if not api_key or OpenAI is None:
        # Fallback deterministic template (no external calls)
        base = f"Grade {grade} {level} Passage. " \
               f"This is a placeholder passage of approximately {lo}–{hi} words. "
        detail = "It introduces a clear main idea and uses simple sequencing words (first, then, finally). "
        if level.lower().startswith("extension"):
            detail = "It introduces a main idea with a mild inference and uses varied connectors (meanwhile, however, therefore). "
        kw = f" Keywords included: {keywords}." if keywords else ""
        lo_text = f" Learning outcomes: {learning_outcomes}." if learning_outcomes else ""
        body = ("In a small town near a quiet river, students prepared for a class project about local history. "
                "They visited a museum, read signs carefully, and asked questions about the objects they saw. "
                "Some items were tools used by families long ago; others were fossils found in nearby hills. "
                "As they took notes, they noticed how each object told a part of a bigger story, showing how people lived, "
                "worked, and learned from their surroundings. ")
        return base + detail + body + kw + lo_text

    client = OpenAI(api_key=api_key)
    # Models change over time; choose a capable, cost-effective chat model
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    try:
        resp = client.chat.completions.create(
            model=model_name,
            temperature=0.7,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt.strip()}
            ]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        # Graceful fallback
        return f"(Local fallback; API unavailable)\n\n" + generate_passage(grade, level, length, keywords, learning_outcomes="").strip()
