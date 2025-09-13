import re
from typing import List
from .nlp import get_nlp
from .constants import SUPPORTED_ENTS

def split_sentences(text: str) -> List[str]:
    nlp = get_nlp()
    doc = nlp(text)
    return [s.text.strip() for s in doc.sents if s.text.strip()]

def pick_key_sentences(text: str, k: int = 8) -> List[str]:
    nlp = get_nlp()
    doc = nlp(text)
    scored = []
    for sent in doc.sents:
        s = sent.text.strip()
        if not s:
            continue
        ents = [ent for ent in sent.ents if ent.label_ in SUPPORTED_ENTS]
        score = len([t for t in sent if t.is_alpha and not t.is_stop]) + 3*len(ents)
        scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    uniq, seen = [], set()
    for _, s in scored:
        if s not in seen:
            uniq.append(s); seen.add(s)
        if len(uniq) >= k:
            break
    return uniq

def highlight_span(sentence: str, span: str) -> str:
    if not span:
        return sentence
    pattern = re.compile(re.escape(span), re.IGNORECASE)
    return pattern.sub(lambda m: f"<span class='highlight'>{m.group(0)}</span>", sentence, count=1)
