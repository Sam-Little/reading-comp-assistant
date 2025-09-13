import random
from typing import Dict, List, Any
from nltk.corpus import wordnet as wn
from .nlp import get_nlp
from .constants import WH_TAGS, SUPPORTED_ENTS, CLOZE_POS, CLOZE_BLACKLIST

def _synonym_distractors(word: str, pos_hint: str, limit: int = 6) -> List[str]:
    pos_map = {"NOUN": wn.NOUN, "VERB": wn.VERB, "ADJ": wn.ADJ, "ADV": wn.ADV}
    wn_pos = pos_map.get(pos_hint, None)
    cands = set()
    if wn_pos:
        for syn in wn.synsets(word, pos=wn_pos):
            for lemma in syn.lemmas():
                txt = lemma.name().replace("_", " ").lower()
                if txt != word.lower():
                    cands.add(txt)
    return list(cands)[:limit]

def _entity_distractors(doc, target_ent, limit=6):
    cands = {ent.text for ent in doc.ents if ent.label_ == target_ent.label_ and ent.text != target_ent.text}
    return list(cands)[:limit]

def make_cloze_from_sentence(sent_text: str) -> Dict[str, Any]:
    nlp = get_nlp()
    sent_doc = nlp(sent_text)
    candidates = [t for t in sent_doc if t.pos_ in CLOZE_POS and t.lemma_.lower() not in CLOZE_BLACKLIST and t.is_alpha]
    if not candidates:
        return {}
    token = random.choice(candidates)
    answer = token.text
    prompt = sent_text.replace(token.text, "____", 1)
    return {
        "qtype": "cloze",
        "prompt": f"Fill in the blank: {prompt}",
        "options": [],
        "correct_answer": answer,
        "evidence": sent_text
    }

def make_wh_from_sentence(sent_text: str, passage_text: str) -> Dict[str, Any]:
    nlp = get_nlp()
    doc = nlp(passage_text)
    sent_doc = nlp(sent_text)
    ents = [ent for ent in sent_doc.ents if ent.label_ in SUPPORTED_ENTS]
    if not ents:
        return {}
    ent = random.choice(ents)
    wh = WH_TAGS[ent.label_]
    question = sent_text.replace(ent.text, "____", 1)
    dists = _entity_distractors(doc, ent, limit=6)
    if len(dists) < 3:
        fillers = ["N/A", "Unknown", "Not stated"]
        dists.extend([f for f in fillers if f.lower() != ent.text.lower()])
    options = [ent.text] + dists[:3]
    random.shuffle(options)
    return {
        "qtype": "wh_mcq",
        "prompt": f"{wh} is missing in the sentence: {question}",
        "options": options,
        "correct_answer": ent.text,
        "evidence": sent_text
    }

def generate_questions(passage_text: str, n: int = 6) -> List[Dict[str, Any]]:
    from .utils import pick_key_sentences
    key_sents = pick_key_sentences(passage_text, k=max(n*2, 8))
    random.shuffle(key_sents)
    questions = []
    cloze_needed = max(1, n // 2)
    wh_needed = n - cloze_needed
    for s in key_sents:
        if cloze_needed > 0:
            q = make_cloze_from_sentence(s)
            if q:
                questions.append(q); cloze_needed -= 1
                if len(questions) >= n: break
                continue
        if wh_needed > 0:
            q = make_wh_from_sentence(s, passage_text)
            if q:
                questions.append(q); wh_needed -= 1
                if len(questions) >= n: break
                continue
    for s in key_sents:
        if len(questions) >= n: break
        q = make_cloze_from_sentence(s) or make_wh_from_sentence(s, passage_text)
        if q: questions.append(q)
    for i, q in enumerate(questions):
        q["id"] = f"q{i+1}"
    return questions[:n]
