import spacy

# Ensure the 'en_core_web_lg' model is installed and load it
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    from spacy.cli import download
    download("en_core_web_lg")  # Download the model if not already installed
    nlp = spacy.load("en_core_web_lg")

def lemmatize_word(word):
    """
    Lemmatizes the given word using the SpaCy NLP pipeline.
    Args:
    - word (str): The word to lemmatize.
    Returns:
    - str: The lemma of the word.
    """
    doc = nlp(word)
    return doc[0].lemma_  # Returning the lemma of the first token in the processed word.

if __name__ == "__main__":
    word_to_lemmatize = input("Enter a word to lemmatize: ").strip()
    lemma = lemmatize_word(word_to_lemmatize)
    print(f"Lemma of '{word_to_lemmatize}': {lemma}")
