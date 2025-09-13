from typing import Dict, Any
from rapidfuzz import fuzz
from .nlp import get_nlp
from .constants import RAPIDFUZZ_THRESHOLD

def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())

def _lemma_pipe(text: str) -> str:
    nlp = get_nlp()
    doc = nlp(text)
    toks = [t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop]
    return " ".join(toks)

def grade_mcq(user_answer: str, correct_answer: str) -> Dict[str, Any]:
    is_correct = _normalize(user_answer) == _normalize(correct_answer)
    return {"is_correct": is_correct, "score": 1.0 if is_correct else 0.0}

def grade_short_answer(user_answer: str, correct_answer: str) -> Dict[str, Any]:
    gold_lemmas = _lemma_pipe(correct_answer)
    user_lemmas = _lemma_pipe(user_answer)
    if not user_lemmas:
        return {"is_correct": False, "score": 0.0}
    sim = fuzz.token_set_ratio(user_lemmas, gold_lemmas)
    is_correct = sim >= RAPIDFUZZ_THRESHOLD
    score = 1.0 if is_correct else (0.5 if 70 <= sim < RAPIDFUZZ_THRESHOLD else 0.0)
    return {"is_correct": is_correct, "score": score, "similarity": sim}
