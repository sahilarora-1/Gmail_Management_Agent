import pickle
import re

# Load model and vectorizer
model = pickle.load(open("spam_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

def clean_text(text):
    # Basic cleaning
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def is_spam(email_text, threshold=0.8):
    vec = vectorizer.transform([email_text])
    if hasattr(model, "predict_proba"):
        prob = model.predict_proba(vec)[0][1]  # probability of spam
        return prob >= threshold
    else:
        # fallback: use hard prediction
        return model.predict(vec)[0] == 1