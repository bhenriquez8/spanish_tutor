from deepl_client import translate_with_deepl
from engine import get_sentences, detect_tense, compare_translation, generate_feedback, normalize_sentence
import json

if __name__ == "__main__":
    with open("sentences.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        category = int(input("Which would you like to translate [0] Preterite, [1] Imperfect: "))
        if category not in (0,1):
            raise ValueError
    except ValueError:
        print("Invalid input. Please enter 0 or 1.")
        return

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

    user_tense = detect_tense(user_words)
    deepl_tense = detect_tense(deepl_words)

    result = compare_translation(
        user_words,
        deepl_words,
        user_tense,
        deepl_tense
    )

    feedback = generate_feedback(result, deepl_translation, deepl_tense)
    print(feedback)
