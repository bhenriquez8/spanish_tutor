import requests
from dotenv import dotenv_values

secrets = dotenv_values(".env")
DEEPL_API_KEY = secrets["API_KEY"]
DEEPL_URL = "https://api-free.deepl.com/v2/translate"

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

