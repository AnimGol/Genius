import spacy
import os
import pandas as pd

# Load SpaCy NLP model
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    from spacy.cli import download
    download("en_core_web_lg")
    nlp = spacy.load("en_core_web_lg")

# Function to lemmatize words
def lemmatize_word(word):
    """
    Lemmatizes the given word using SpaCy NLP pipeline.
    Args:
    - word (str): The word to lemmatize.
    Returns:
    - str: The lemma of the word.
    """
    if pd.isna(word) or word.strip() == "":  # Handle missing values
        return "UNKNOWN"
    
    doc = nlp(word)
    return doc[0].lemma_  # Return lemma of the first token

# Get file ID from user
print("Please write the ID (e.g., 10 or 14). Choose a number available in the folder 'SPGC-counts-2018-07-18'.")
id = input().strip()

# Define file path
text_folder_path = "SPGC-counts-2018-07-18"
file_name = f"PG{id}_counts.txt"
full_path = os.path.join(text_folder_path, file_name)

# Check if file exists
if not os.path.exists(full_path):
    print(f"Error: File '{full_path}' not found!")
    exit()

# Read file
df = pd.read_csv(full_path, delimiter="\t")  # Adjust delimiter if necessary
print(f"File '{file_name}' found and read successfully!")

# Ensure 'Word' column exists
if "Word" not in df.columns:
    print("Error: The file does not contain a 'Word' column.")
    exit()

# Print original row count
print(f"Original number of rows: {len(df)}")

# Fill missing values before processing
df["Word"] = df["Word"].fillna("UNKNOWN")

# Apply lemmatization
df["Lemma"] = df["Word"].apply(lemmatize_word)

# Print processed row count
print(f"Processed number of rows: {len(df)}")

# Save output file
output_file = f"PG{id}_counts_with_lemmas.txt"
output_path = os.path.join(text_folder_path, output_file)
df.to_csv(output_path, sep="\t", index=False)

print(f"Lemmatized data saved as '{output_file}'.")

