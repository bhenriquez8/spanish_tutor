import json
import random
import deepl
from dotenv import dotenv_values

secrets=dotenv_values(".env")
DEEPL_API_KEY = secrets["API_KEY"]

def translate_with_deepl(eng_sentence="Hello, world"):
    if not DEEPL_API_KEY:
        return None

    deepl_client = deepl.DeepLClient(DEEPL_API_KEY)

    result = deepl_client.translate_text(eng_sentence, target_lang="ES")
    print(result.text)


def get_sentences(data, category, count):
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

def display_menu():
    print("==========================================")
    print("|------------Select a Category------------|")
    print("==========================================")
    print("| Option [0]: Preterite                   |")
    print("| Option [1]: Imperfect                   |")
    print("| (random # of English sentences awaits!) |")
    print("|                                         |")
    print("| Enter your choice! 0 or 1               |")
    print("==========================================")
    
if __name__ == "__main__":
    with open("sentences.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    """
    categories = ["preterite", "imperfect"]

    display_menu()
    choice = int(input("Enter: "))
    amount = random.randint(1, 10)

    sentences = get_sentences(data, categories[choice], amount)
    incorrect_counter = 0

    for s in sentences:
        print(f"Translate into Spanish: '{s["english"]}'")
        translation = input()

        if translation.lower() != s['spanish'].lower():
            incorrect_counter = incorrect_counter + 1
            print(f"Oops! Here's the correct translation: '{s["spanish"]}'")

    if incorrect_counter == 0:
        print("Wow! Perfect score!")
    else:
        print(f"Completed! You got '{amount-incorrect_counter}/{amount}' correct!")
    """
    translate_with_deepl()
