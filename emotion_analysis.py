import os
import csv
import subprocess
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.corpus import stopwords

# Ensure necessary packages are installed
try:
    from wordcloud import WordCloud
except ImportError:
    subprocess.check_call(["pip", "install", "wordcloud"])
    from wordcloud import WordCloud

try:
    import spacy
    from spacy.cli import download
except ImportError:
    subprocess.check_call(["pip", "install", "spacy"])
    import spacy
    from spacy.cli import download

# Ensure the 'en_core_web_lg' model is installed and load it
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    download("en_core_web_lg")  # Download the model if not already installed
    nlp = spacy.load("en_core_web_lg")

# Download NLTK stopwords
nltk.download('stopwords')

def lemmatize_word(word):
    """Return the lemma of a word using spaCy."""
    doc = nlp(word)
    return doc[0].lemma_

def emotion_dictionary(file_path):
    emotion_lexicon = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            word, emotion, value = line.strip().split('\t')
            if value == '1':
                if word not in emotion_lexicon:
                    emotion_lexicon[word] = []
                emotion_lexicon[word].append(emotion)
    return emotion_lexicon

def analysis(full_path, emotion_lexicon):
    second_lexicon = {}
    with open(full_path, 'r', encoding='utf-8') as file:
        for line in file:
            word, count = line.strip().split('\t')
            lemma = lemmatize_word(word)  # Get lemma
            emotions = emotion_lexicon.get(lemma, emotion_lexicon.get(word, []))  # Check lemma first, then word
            second_lexicon[word] = (int(count), emotions)
    return second_lexicon

def emotion_frequency(output_path):
    emotions_in_text = {}
    with open(output_path) as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        next(reader)   # Skip the header row
        for row in reader:
            word, number, emotions = row
            separated_emotions = emotions.strip().split(',')
            for emotion in separated_emotions:
                if emotion in ['anticipation', 'joy', 'positive', 'surprise', 'trust', 'anger', 'negative', 'disgust', 'fear', 'sadness']:
                    if emotion in emotions_in_text:
                        emotions_in_text[emotion] += int(number)
                    else:
                        emotions_in_text[emotion] = int(number)
    return emotions_in_text

def words_info(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        x = 0
        Words_dict = {}
        for line in file:
            if x < 50:
                word, number = line.strip().split('\t')
                if word not in Words_dict:
                    Words_dict[word] = []
                Words_dict[word].append(number)
                x += 1
            else:
                break
    return Words_dict

def sum_counts(full_path):
    with open(full_path, 'r', encoding='utf-8') as file:
        total = 0
        for line in file:
            word, count = line.strip().split('\t')
            total += int(count)
    return total

def main():
    print("Please write the ID (e.g., 10 or 14). Please choose a number that is available in the folder of Counts.")
    id = input().strip()
    text_folder_path = r"SPGC-counts-2018-07-18"
    file_name = f"PG{id}_counts.txt"
    full_path = os.path.join(text_folder_path, file_name)

    # Open and read the file
    with open(full_path, "r") as file:
        content = file.read()
        print('File is found and read successfully!')

    emotion_lexicon = emotion_dictionary(r'NRC-Emotion-Lexicon-Wordlevel-v0.92.txt')
    text_result = analysis(full_path, emotion_lexicon)

    output_file = f"emotion_analysis_{id}.tsv"
    output_dir = r"results"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, output_file)

    with open(output_path, 'w', newline='', encoding='utf-8') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        writer.writerow(['Word', 'Count', 'Emotions'])
        for word, (count, emotions) in text_result.items():
            writer.writerow([word, count, ', '.join(emotions)])

    print(f"Emotion analysis saved to {output_path}")

    emotions_in_text = emotion_frequency(output_path)
    emotions = list(emotions_in_text.keys())
    values = list(emotions_in_text.values())
    sns.set(style="whitegrid")

    # Create a bar chart
    plt.figure(figsize=(10, 6))  # Set the figure size
    bars = plt.bar(emotions, values, color=sns.color_palette("Blues", n_colors=len(emotions)))

    # Adding titles and labels
    plt.title('Emotion Frequency Distribution', fontsize=18, weight='bold', family='serif')
    plt.xlabel('Emotions', fontsize=12, weight='bold', family='serif')
    plt.ylabel('Frequency', fontsize=12, weight='bold', family='serif')

    # Rotate the x-axis labels for better visibility
    plt.xticks(rotation=45, fontsize=12)

    # Adding grid lines to make the chart more readable
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 100, round(yval, 0), ha='center', va='bottom', fontsize=10)

    # Display the chart
    plt.tight_layout()
    plt.savefig(f"barchart{id}.png")
    print('The barchart is saved.')

    Most_frequent_words = words_info(full_path)
    cleaned_data = {word: int(numbers[0]) for word, numbers in Most_frequent_words.items()}
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(cleaned_data)

    # Display the word cloud using matplotlib
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # Turn off the axis
    plt.show()

    # Save the word cloud as a PNG file
    output_wordcloud_file = f"
::contentReference[oaicite:0]{index=0}
 
