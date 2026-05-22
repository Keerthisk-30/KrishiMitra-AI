import spacy
# Load NLP model
nlp = spacy.load("en_core_web_sm")
def extract_keywords(text):
    doc = nlp(text)
    keywords = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"]:
            keywords.append(token.text)
    unique_keywords = list(set(keywords))
    return ", ".join(unique_keywords)