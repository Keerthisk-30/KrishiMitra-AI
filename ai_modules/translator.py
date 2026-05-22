from deep_translator import GoogleTranslator
from langdetect import detect


def detect_language(text):
    try:
        language = detect(text)
        supported_languages = [
            'en',
            'kn',
            'te',
            'ta',
            'hi'
        ]
        if language not in supported_languages:
            return 'en'
        return language
    except:
        return 'en'


def translate_to_english(text):
    try:
        language = detect_language(text)
        if language == 'en':
            return text
        translated = GoogleTranslator(
            source='auto',
            target='en'
        ).translate(text)
        return translated
    except:
        return text

def translate_back(text, target_language):
    try:
        translated = GoogleTranslator(
            source='en',
            target=target_language
        ).translate(text)
        return translated
    except:
        return text
    
# -----------------------------------------
# NORMALIZE CROP NAMES
# -----------------------------------------

def normalize_text(crop):

    crop = crop.lower().strip()

    crop_map = {

        # ---------------------------------
        # RICE
        # ---------------------------------

        "ಅಕ್ಕಿ": "Rice",
        "धान": "Rice",
        "rice": "Rice",

        # ---------------------------------
        # WHEAT
        # ---------------------------------

        "ಗೋಧಿ": "Wheat",
        "गेहूं": "Wheat",
        "wheat": "Wheat",

        # ---------------------------------
        # COTTON
        # ---------------------------------

        "ಹತ್ತಿ": "Cotton",
        "कपास": "Cotton",
        "cotton": "Cotton",

        # ---------------------------------
        # TOMATO
        # ---------------------------------

        "ಟೊಮ್ಯಾಟೊ": "Tomato",
        "टमाटर": "Tomato",
        "tomato": "Tomato",

        # ---------------------------------
        # BANANA
        # ---------------------------------

        "ಬಾಳೆ": "Banana",
        "केला": "Banana",
        "banana": "Banana",

        # ---------------------------------
        # MAIZE
        # ---------------------------------

        "ಮೆಕ್ಕೆಜೋಳ": "Maize",
        "मक्का": "Maize",
        "maize": "Maize",

        # ---------------------------------
        # SUNFLOWER
        # ---------------------------------

        "ಸೂರ್ಯಕಾಂತಿ": "Sunflower",
        "सूरजमुखी": "Sunflower",
        "sunflower": "Sunflower",

        # ---------------------------------
        # SUGARCANE
        # ---------------------------------

        "ಕಬ್ಬು": "Sugarcane",
        "गन्ना": "Sugarcane",
        "sugarcane": "Sugarcane",

        # ---------------------------------
        # ONION
        # ---------------------------------

        "ಈರುಳ್ಳಿ": "Onion",
        "प्याज": "Onion",
        "onion": "Onion",

        # ---------------------------------
        # POTATO
        # ---------------------------------

        "ಆಲೂಗಡ್ಡೆ": "Potato",
        "आलू": "Potato",
        "potato": "Potato",

        # ---------------------------------
        # CHILLI
        # ---------------------------------

        "ಮೆಣಸಿನಕಾಯಿ": "Chilli",
        "मिर्च": "Chilli",
        "chilli": "Chilli",

        # ---------------------------------
        # COCONUT
        # ---------------------------------

        "ತೆಂಗು": "Coconut",
        "नारियल": "Coconut",
        "coconut": "Coconut",

        # ---------------------------------
        # GROUNDNUT
        # ---------------------------------

        "ಕಡಲೆಕಾಯಿ": "Groundnut",
        "मूंगफली": "Groundnut",
        "groundnut": "Groundnut",

        # ---------------------------------
        # BRINJAL
        # ---------------------------------

        "ಬದನೆಕಾಯಿ": "Brinjal",
        "बैंगन": "Brinjal",
        "brinjal": "Brinjal",

        # ---------------------------------
        # MILLET
        # ---------------------------------

        "ಸಜ್ಜೆ": "Millet",
        "बाजरा": "Millet",
        "millet": "Millet",

        # ---------------------------------
        # CARROT
        # ---------------------------------

        "ಗಜ್ಜರಿ": "Carrot",
        "गाजर": "Carrot",
        "carrot": "Carrot",

        # ---------------------------------
        # ARECANUT
        # ---------------------------------

        "ಅಡಿಕೆ": "Arecanut",
        "सुपारी": "Arecanut",
        "arecanut": "Arecanut",
        "betel nut": "Arecanut"
    }

    return crop_map.get(
        crop,
        crop.title()
    )