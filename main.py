import json
import random
import requests
import re
from dotenv import dotenv_values

secrets=dotenv_values(".env")
DEEPL_API_KEY = secrets["API_KEY"]
DEEPL_URL = "https://api-free.deepl.com/v2/translate"

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

def translate_with_deepl(eng_sentence="Hello, world"):
    if not DEEPL_API_KEY:
        return None

    data = {
        "auth_key": DEEPL_API_KEY,
        "text": eng_sentence,
        "source_lang": "EN",
        "target_lang": "ES"
    }

    try:
        response = requests.post(DEEPL_URL, data=data, timeout=5)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    try:
        result = response.json()
    except ValueError:
        return None

    translations = result.get("translations")
    if not translations:
        return None

    return translations[0].get("text")



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

if __name__ == "__main__":
    with open("sentences.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    category = int(input("Which would you like to translate [0] Preterite, [1] Imperfect: "))
    if not isinstance(category, int) or (category < 0 or category > 1):
        raise ValueError("Not a valid input. Only enter 0 or 1")

    category = "preterite" if category == 0 else "imperfect"
    rndm_sentence = get_sentences(data, category, 1)
    eng_sentence = rndm_sentence[0]["english"]
    print(f"Translate to Spanish: '{eng_sentence}'")
    user_translation = input("> ")

    deepl_translation = translate_with_deepl(eng_sentence)
    if deepl_translation is None:
        print("Translation sevice is unavailable.")

    user_words = normalize_sentence(user_translation)
    deepl_words = normalize_sentence(deepl_translation)

    print(f"[DEBUG] User words: {user_words}")
    print(f"[DEBUG] DeepL words: {deepl_words}")

    user_tense = detect_tense(user_words)
    deepl_tense = detect_tense(deepl_words)

    print(f"[DEBUG] User tense: {user_tense}")
    print(f"[DEBUG] DeepL tense: {deepl_tense}")

    result = compare_translation(
        user_words,
        deepl_words,
        user_tense,
        deepl_tense
    )

    print(f"[DEBUG] Overlap: {calculate_overlap(user_words, deepl_words):.2f}")
    print(f"[DEBUG] Result: {result}")

    feedback = generate_feedback(result, deepl_translation, deepl_tense)
    print(feedback)
