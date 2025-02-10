import spacy
import os
import pandas as pd

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    from spacy.cli import download
    download("en_core_web_lg")
    nlp = spacy.load("en_core_web_lg")

# Function to lemmatize a word
def lemmatize_word(word):
    doc = nlp(word)
    return doc[0].lemma_ if doc else word  # Ensure it returns the original word if empty

# Get user input for file ID
print("Please write the ID (e.g., 10 or 14). Please choose a number that is available in the folder of Counts.")
id = input().strip()

# Define file path
text_folder_path = "SPGC-counts-2018-07-18"
file_name = f"PG{id}_counts.txt"
full_path = os.path.join(text_folder_path, file_name)

# Check if file exists
if not os.path.exists(full_path):
    print(f"File {file_name} not found!")
else:
    print("File found! Processing...")

    # Read the file into a DataFrame
    df = pd.read_csv(full_path, sep=" ", names=["word", "count"], engine="python")

    # Lemmatize the words
    df["lemma"] = df["word"].apply(lemmatize_word)

    # Save the updated file
    output_file = f"PG{id}_counts_lemmatized.txt"
    df.to_csv(os.path.join(text_folder_path, output_file), sep=" ", index=False)

    print(f"Lemmatized file saved as {output_file}")


