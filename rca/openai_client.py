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
    
    # Use st.secrets to securely access the Gemini API key
    api_key = st.secrets.get("GOOGLE_API_KEY")

    if not api_key:
        return "(Local fallback: no GOOGLE_API_KEY set. Set it in your shell or Streamlit Secrets.)"

    try:
        # Configure the Google API client
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=SYSTEM_PROMPT)

        resp = model.generate_content(user_prompt.strip(),
                                      generation_config=genai.GenerationConfig(temperature=0.7))
        
        return resp.text.strip()
    except Exception as e:
        return f"(Local fallback due to error)\nError: {e}\n\n{traceback.format_exc()}"
