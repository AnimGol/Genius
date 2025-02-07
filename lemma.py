import spacy
import os

def lemmatize_text(file_path, output_path):
    """
    Reads a text file, lemmatizes each word, and saves the lemmatized version to a new file.
    """
    try:
        nlp = spacy.load("en_core_web_lg")
    except OSError:
        print("Downloading 'en_core_web_lg' model...")
        from spacy.cli import download
        download("en_core_web_lg")
        nlp = spacy.load("en_core_web_lg")
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return
    
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    
    doc = nlp(text)
    lemmatized_text = " ".join([token.lemma_ for token in doc])
    
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(lemmatized_text)
    
    print(f"Lemmatized text saved to {output_path}")

# Example usage:
input_file = "path/to/your/input.txt"  # Change this to your actual file path
output_file = "path/to/your/output_lemmatized.txt"  # Change this as needed
lemmatize_text(input_file, output_file)
