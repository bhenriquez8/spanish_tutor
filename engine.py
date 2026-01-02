import random
import re

IMPERFECT_SUFFIXES = (
    "aba", "abas", "ábamos", "aban",
    "ía", "ías", "íamos", "ían"
)

PRETERITE_SUFFIXES = (
    "é", "aste", "ó", "amos", "aron",
    "í", "iste", "ió", "imos", "ieron"
)

IRREGULAR_TENSES = {
    "era": "imperfect",
    "eras": "imperfect",
    "éramos": "imperfect",
    "eran": "imperfect",

    "iba": "imperfect",
    "ibas": "imperfect",
    "iban": "imperfect",

    "veía": "imperfect",
    "veían": "imperfect",

    "fue": "preterite",
    "fueron": "preterite",
    "estuvo": "preterite",
    "tuvo": "preterite",
    "hizo": "preterite",
    "dijo": "preterite"
}

OVERLAP_THRESHOLD = 0.6

def get_sentences(data, category, count=1):
    # Validate top-level structure
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")

    if "categories" not in data or not isinstance(data["categories"], dict):
        raise ValueError("Missing or invalid 'categories' key")

    categories = data["categories"]

    if category not in categories:
        raise ValueError(f"Category '{category}' has no sentences")

    sentences = categories[category]

    if not isinstance(sentences, list) or not sentences:
        raise ValueError(f"Category '{category}' has no sentences")

    # Filter only valid sentence objects
    valid_sentences = []
    for s in sentences:
        if isinstance(s, dict) and isinstance(s.get("english"), str):
            valid_sentences.append(s)

    if not valid_sentences:
        raise ValueError(f"No valid sentences found in '{category}'")

    # Adjust count safely
    count = min(count, len(valid_sentences))
    
    return random.sample(valid_sentences, count)

def normalize_sentence(sentence):
    sentence = sentence.lower()
    sentence = re.sub(r'[^\w\s]', '', sentence)
    sentence = sentence.strip()
    words = sentence.split()
    return words

def detect_tense(words):
    for word in words:
        # Check irregulars first
        if word in IRREGULAR_TENSES:
            return IRREGULAR_TENSES[word]

        # Check imperfect suffixes
        for suffix in IMPERFECT_SUFFIXES:
            if word.endswith(suffix):
                return "imperfect"

        # Check preterise suffixes
        for suffix in PRETERITE_SUFFIXES:
            if word.endswith(suffix):
                return "preterite"

    return "unknown"

def compare_translation(user_words, deepl_words, user_tense, deepl_tense):
    # Rule 1: Exact match
    if user_words == deepl_words:
        return "perfect"

    overlap = calculate_overlap(user_words, deepl_words)

    # Rule 2: High overlap (meaning likely correct)
    if overlap >= OVERLAP_THRESHOLD:
        if user_tense == deepl_tense:
            return "correct_different_phrasing"
        else:
            return "tense_mismatch"

    # Rule 3: Incorrect meaning
    return "incorrect"

def calculate_overlap(user_words, deepl_words):
    user_set = set(user_words)
    deepl_set = set(deepl_words)

    shared = user_set & deepl_set

    if not deepl_set:
        return 0.0

    return len(shared) / len(deepl_set)

def generate_feedback(result, deepl_translation, deepl_tense):
    if result == "perfect":
        return "Correct! Nice work."

    if result == "correct_different_phrasing":
        return "Correct meaning. Your phrasing is different, but it works."

    if result == "tense_mismatch":
        if deepl_tense == "imperfect":
            return (
                "Good translation, but this sentence uses the imperfect, "
                "not the preterite"
            )
        elif deepl_tense == "preterite":
            return (
                "Good translation, but this sentence uses the preterite, "
                "not the imperfect."
            )
        else:
            return "Good translation, but the tense could not be evaluated."

    if result == "incorrect":
        return "Not quite. Suggested translation: " + deepl_translation

    return "Unable to evaluate this sentence."

