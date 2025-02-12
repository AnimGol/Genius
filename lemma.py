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

    # Read the file into a DataFrame, skipping the first row (header)
    df = pd.read_csv(full_path, sep="\t", names=["word", "count"], engine="python", header=None, skiprows=1)

    # Lemmatize the words
    df["lemma"] = df["word"].apply(lemmatize_word)

    # Create a new DataFrame with only the lemma and count columns
    df_final = df[["lemma", "count"]]

    # Save the updated file without headers
    output_file = f"PG{id}_counts_lemmatized.txt"
    df_final.to_csv(os.path.join(text_folder_path, output_file), sep="\t", index=False, header=False)

    print(f"Lemmatized file saved as {output_file}")
