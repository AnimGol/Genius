import os
import spacy

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

# Automatically get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "input_text.txt")  # Text to lemmatize
output_file = os.path.join(script_dir, "lemmatized_text.txt")  # Output

def lemmatize_text(text):
    """Lemmatize the input text using spaCy."""
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc])

def process_file():
    """Reads input file, lemmatizes text, and saves output."""
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return
    
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    lemmatized_text = lemmatize_text(text)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(lemmatized_text)
    
    print(f"Lemmatized text saved to: {output_file}")

if __name__ == "__main__":
    process_file()
