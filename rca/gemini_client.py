import os, traceback
from typing import Optional
import streamlit as st
import google.generativeai as genai

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

    # prefer Streamlit secrets, fall back to environment variable
    api_key = st.secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    def _local_generator():
        """Deterministic simple local fallback passage (guarantees output)."""
        kw_text = f" It includes: {keywords}." if keywords else ""
        lo_text = f" It supports: {learning_outcomes}." if learning_outcomes else ""
        base = (f"A short passage for Grade {grade}, Level {level}. Sam went to the park and "
                "saw birds, trees, and a small pond. He listened to the birds and counted five ducks. "
                "He learned that nature can be quiet and interesting. "
                "The story is simple and helps young readers practise reading skills.")
        text = base + kw_text + lo_text
        words = text.split()
        # expand to reach approximate lower bound if needed
        add = " The children learned a little more about the world around them."
        while len(words) < lo:
            text += add
            words = text.split()
            if len(words) >= hi:
                break
        # trim if overshoot
        if len(words) > hi:
            text = " ".join(words[:hi])
            if not text.endswith("."):
                text = text.rstrip(",; ") + "."
        return text.strip()

    if not api_key:
        return "(Local fallback: no GOOGLE_API_KEY set.)\n\n" + _local_generator()

    try:
        # configure client
        genai.configure(api_key=api_key)

        # pick a model that supports generateContent
        chosen = None
        try:
            for m in genai.list_models():
                # support varied SDK shapes
                name = getattr(m, "name", None) or getattr(m, "model", None) or str(m)
                methods = getattr(m, "supported_generation_methods", None) or []
                # some SDKs give strings; normalize
                if isinstance(methods, (list, tuple)) and "generateContent" in methods:
                    chosen = name
                    break
                # fallback: some metadata lists methods as strings inside a dict
                if isinstance(methods, str) and "generateContent" in methods:
                    chosen = name
                    break
        except Exception:
            chosen = None

        if not chosen:
            # no usable model found for this key/project
            st.warning("No usable generateContent-capable model found for this API key. Using local fallback.")
            return "(Local fallback: no usable model found.)\n\n" + _local_generator()

        # call chosen model
        model = genai.GenerativeModel(chosen, system_instruction=SYSTEM_PROMPT)
        resp = model.generate_content(user_prompt.strip(),
                                      generation_config=genai.GenerationConfig(temperature=0.7))

        # unwrap response safely (SDKs differ)
        text = getattr(resp, "text", None)
        if not text:
            try:
                # try common alternate shapes
                text = resp.candidates[0].content[0].text
            except Exception:
                try:
                    # resp.candidates -> list of dicts with 'output' or similar
                    text = str(resp)
                except Exception:
                    text = None

        if not text or len(text.split()) < 6:
            # model returned nothing meaningful; fallback
            st.warning("Model returned empty or too short content. Using local fallback.")
            return "(Local fallback: model returned empty.)\n\n" + _local_generator()

        return text.strip()

    except Exception as e:
        # log the error in Streamlit and return a local fallback so the app stays usable
        st.error(f"Model call failed: {e}")
        return f"(Local fallback due to error: {e})\n\n" + _local_generator()
