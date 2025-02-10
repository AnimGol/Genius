import os
import csv
import subprocess

try: 
    from wordcloud import WordCloud
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "wordcloud"])
    from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
try:    
    import nltk
except ImportError:
    subprocess.check_call(["pip", "install", "nltk"])
    import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
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

print ("Please write the ID (e.g., 10 or 14). Please choose a number that is availavle in the folder of Counts.")
id = input (). strip ()
text_folder_path = r"SPGC-counts-2018-07-18"
file_name = f"PG{id}_counts.txt"
full_path = os.path.join(text_folder_path, file_name)  # Combine folder and file name

    # Open and read the file
with open(full_path, "r") as file:
    content = file.read()
    print ('file is found and read successfully!')

def emotion_dictionary (file_path):
    emotion_lexicon = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
                    # strip(), ensures that any unnecessary whitespace or special characters (like \n, spaces or \t at the beginning or end of strings) at the beginning or end of each line are removed, leading to more accurate data processing.
            word, emotion, value = line.strip().split('\t')
            if value == '1':
                if word not in emotion_lexicon:
                    emotion_lexicon[word] = []
                emotion_lexicon[word].append(emotion)
    return emotion_lexicon
result = emotion_dictionary(r'NRC-Emotion-Lexicon-Wordlevel-v0.92.txt')
# print (result)

def analysis(full_path):
    second_lexicon = {}
    with open(full_path, 'r', encoding='utf-8') as file:
        for line in file:
            word, count = line.strip().split('\t')
            emotions = result.get(word, [])  # Get emotions if the word exists in the emotion lexicon
            second_lexicon[word] = (int(count), emotions) 
    return second_lexicon

        
text_result = analysis (full_path)
# print (text_result)

output_file = f"emotion_analysis_{id}.tsv"
output_dir = r"results"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
output_path = os.path.join(r"results", output_file)

with open(output_path, 'w', newline='', encoding='utf-8') as tsv_file:
    writer = csv.writer(tsv_file, delimiter='\t')
    # Write header
    writer.writerow(['Word', 'Count', 'Emotions'])
    # Write data
    for word, (count, emotions) in text_result.items():
        writer.writerow([word, count, ', '.join(emotions)])

print(f"Emotion analysis saved to {output_path}")


def emotion_frequency (output_path):
            emotions_in_text = {}
            with open (output_path) as tsv_file:
                reader = csv.reader (tsv_file, delimiter='\t')
                next (reader)   # Skip the header row
                for row in reader:
                    word, number, emotions = row
                    separated_emotions= emotions.strip().split(',')
                    for emotion in separated_emotions:
                        if emotion in ['anticipation', 'joy', 'positive', 'surprise', 'trust', 'anger', 'negative', 'disgust', 'fear', 'sadness']:
                          # Increment the count for the emotion
                            if emotion in emotions_in_text:
                                   emotions_in_text[emotion] += int(number)
                            else:
                                   emotions_in_text[emotion] = int(number)
            return emotions_in_text
        
emotion_frequency =  emotion_frequency (output_path) 
print (emotion_frequency)

def total_emotion_count (emotion_frequency):
    total = sum (emotion_frequency.values())
    return total

def add_percentage_to_emotions(emotion_frequency):
    total_count = total_emotion_count(emotion_frequency)
    emotion_percentage = {}
    for emotion, count in emotion_frequency.items():
        percentage = (count / total_count) * 100  
        emotion_percentage[emotion] = percentage
    return emotion_percentage

percentages = add_percentage_to_emotions (emotion_frequency)


def save_emotion_results (emotion_frequency, percentages, outputfile):
    with open(outputfile, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(['Emotion', 'Count', 'Percentage'])  # Write header
        for emotion in emotion_frequency:
            count = emotion_frequency[emotion]  # Get the count for the emotion
            percentage = percentages.get(emotion, 0)  # Get the percentage for the emotion
            writer.writerow([emotion, count, round(percentage, 2)])  # Write the count and percentage



save_emotions_percentage = f"emotion_percentage_{id}.tsv"
y = os.path.join(r"results", save_emotions_percentage)
save = save_emotion_results (emotion_frequency, percentages, y)
print(f"emotion percentage saved to {y}")

emotions = list(emotion_frequency.keys())
values = list(emotion_frequency.values())
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
  plt.text(bar.get_x() + bar.get_width()/2, yval + 100, round(yval, 0), ha='center', va='bottom', fontsize=10)

# Display the chart
plt.tight_layout()
# plt.show()        
plt.savefig(os.path.join(output_dir, f"barchart{id}.png"))
print ('The barchart is saved.')


def words_info (file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        x = 0
        Words_dict = {}
        for line in file:
            if x < 50: 
                word, number = line. strip ().split ('\t')
                if word not in Words_dict:
                    Words_dict[word] = []
                Words_dict [word].append (number)
                x += 1
            else:
              break
    return Words_dict

Most_frequent_words = words_info (full_path)
# print (Most_frequent_words)

cleaned_data = {word: int(numbers[0]) for word, numbers in Most_frequent_words.items()}
wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(cleaned_data)

# Display the word cloud using matplotlib
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # Turn off the axis
plt.show()

# Save the word cloud as a PNG file
output_wordcloud_file = f"wordcloud_{id}.png"
output_wordcloud_path = os.path.join(output_dir, output_wordcloud_file)
wordcloud.to_file(os.path.join(output_dir, f"wordcloud_{id}.png"))

print(f"Word cloud saved to {output_wordcloud_path}")

# Here we have a set or collection of stopwords in English:
stop_words = set(stopwords.words('english'))  
cleaned_nonstop_data = {word: count for word, count in cleaned_data.items() if word.lower() not in stop_words}
top_10_nonstop_words = dict(sorted(cleaned_nonstop_data.items(), key=lambda item: item[1], reverse=True)[:10])

wordcloud_nonstop = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(top_10_nonstop_words)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud_nonstop, interpolation='bilinear')
plt.axis('off')
plt.show()

# Save the non-stop word cloud
output_wordcloud_nonstop_file = f"wordcloud_nonstop_{id}.png"
output_wordcloud_nonstop_path = os.path.join(output_dir, output_wordcloud_nonstop_file)
wordcloud_nonstop.to_file(os.path.join(output_dir, f"wordcloud_nonstop_{id}.png"))

print(f"Non-stop word cloud saved to {output_wordcloud_nonstop_path}")



def sum_counts (full_path ):
    
    with open(full_path, 'r', encoding='utf-8') as file:
        total = 0
        for line in file:
                    # strip(), ensures that any unnecessary whitespace or special characters (like \n, spaces or \t at the beginning or end of strings) at the beginning or end of each line are removed, leading to more accurate data processing.
            word, count = line.strip().split('\t')
            total += int (count)
    return total


x = sum_counts (full_path)
print ('Word count in this text is ', x)





# Now trying to save the results and then adding the links to our db:
genius1_link = os.path.join(output_dir, f"wordcloud_{id}.png")
genius2_link = os.path.join(output_dir, f"wordcloud_nonstop_{id}.png")
genius3_link = os.path.join(output_dir, f"barchart{id}.png")

# working on interactive features
emotion = input("Enter the emotion you want to search for (e.g., joy, sadness): ").strip()
percentage = float(input("Enter the percentage you're looking for (e.g., 50): ").strip())

result_path = r"results"
# file_name = f"PG{id}_counts.txt"
# full_path = os.path.join(text_folder_path, file_name) 
