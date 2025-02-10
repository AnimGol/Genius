import spacy
import os

print("Please write the ID (e.g., 10 or 14). Please choose a number that is available in the folder of Counts.") 
id = input().strip()
text_folder_path = r"SPGC-counts-2018-07-18"
file_name = f"PG{id}_counts.txt"
full_path = os.path.join(text_folder_path, file_name)  # Combine folder and file name

# Open and read the file
try:
    with open(full_path, "r", encoding="utf-8") as file:
        content = file.read()
        print('File is found and read successfully!')
except FileNotFoundError:
    print(f"Error: The file '{file_name}' was not found in the directory '{text_folder_path}'.")
    exit()

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

# Process the file content by lemmatizing words
words = content.split()  # Tokenize by splitting on spaces
lemmatized_words = [lemmatize_word(word) for word in words]

# Print some lemmatized words for verification
print("Sample of lemmatized words:", lemmatized_words[:10])  # Show first 10 words

# Optional: Save lemmatized words to a new file
lemmatized_file_path = os.path.join(text_folder_path, f"PG{id}_lemmatized.txt")
with open(lemmatized_file_path, "w", encoding="utf-8") as output_file:
    output_file.write(" ".join(lemmatized_words))

print(f"Lemmatized words saved to: {lemmatized_file_path}")

if __name__ == "__main__":
    word_to_lemmatize = input("Enter a word to lemmatize: ").strip()
    lemma = lemmatize_word(word_to_lemmatize)
    print(f"Lemma of '{word_to_lemmatize}': {lemma}")

