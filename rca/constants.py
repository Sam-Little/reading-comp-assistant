WH_TAGS = {
    "PERSON": "Who",
    "ORG": "What organization",
    "GPE": "Where",
    "LOC": "Where",
    "DATE": "When"
}
SUPPORTED_ENTS = set(WH_TAGS.keys())
MIN_SENT_LEN = 8
MAX_SENT_LEN = 45
CLOZE_POS = {"NOUN", "PROPN", "VERB"}
CLOZE_BLACKLIST = {"be", "have", "do"}
CLOZE_COUNT = 3
WH_COUNT = 3
RAPIDFUZZ_THRESHOLD = 85
