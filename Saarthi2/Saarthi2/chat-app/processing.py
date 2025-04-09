import os
import requests
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from utils import LANGUAGE_MAP, LANGUAGES

load_dotenv()
print("Loaded API Key:", os.getenv("GEMINI_API_KEY"))

api_key = os.getenv("GEMINI_API_KEY")

DetectorFactory.seed = 0

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

SUPPORTED_LANGUAGES = GoogleTranslator().get_supported_languages(as_dict=True)

def detect_and_translate_to_english(text):
    """Detects the language and translates to English."""
    try:
        detected_language = detect(text)
        if detected_language not in SUPPORTED_LANGUAGES:
            detected_language = 'en'

        translated_text = text if detected_language == 'en' else GoogleTranslator(source=detected_language, target='en').translate(text)
    except LangDetectException:
        detected_language, translated_text = 'en', text

    return translated_text, detected_language

def translate_to_original_language(text, original_language):
    """Translates text back to the original language."""
    try:
        if original_language not in SUPPORTED_LANGUAGES:
            original_language = 'en'

        return GoogleTranslator(source='en', target=original_language).translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def clean_response(response):
    """Removes markdown asterisks and strips leading/trailing whitespace."""
    return response.replace("*", "").strip()

def get_gemini_response(prompt):
    """Generates a response using Gemini-Pro."""
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    params = {"key": GOOGLE_API_KEY}
    
    response = requests.post(API_URL, headers=headers, params=params, json=data)

    if response.status_code == 200:
        try:
            raw_response = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return clean_response(raw_response)
        except (KeyError, IndexError, TypeError):
            return "Invalid response format from API."
    else:
        return f"Error: {response.status_code}, {response.text}"

def process_text_with_gemini(user_text):
    """Processes the input text through translation and generation pipeline."""
    translated_text, original_language = detect_and_translate_to_english(user_text)
    gemini_response = get_gemini_response(translated_text)
    return translate_to_original_language(gemini_response, original_language)
    return translate_to_original_language(gemini_response, original_language)
