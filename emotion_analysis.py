import os
import csv
try: 
    from wordcloud import WordCloud
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "wordcloud"])
    from wordcloud import WordCloud
import matplotlib.pyplot as plt

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
    
output_path = os.path.join(output_dir, output_file)

with open(output_path, 'w', newline='', encoding='utf-8') as tsv_file:
    writer = csv.writer(tsv_file, delimiter='\t')
    # Write header
    writer.writerow(['Word', 'Count', 'Emotions'])
    # Write data
    for word, (count, emotions) in text_result.items():
        writer.writerow([word, count, ', '.join(emotions)])

print(f"Emotion analysis saved to {output_path}")


def words_info (file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        x = 0
        Words_dict = {}
        for line in file:
            if x < 20: 
                word, number = line. strip ().split ('\t')
                if word not in Words_dict:
                    Words_dict[word] = []
                Words_dict [word].append (number)
                x += 1
            else:
              break
    return Words_dict

Most_frequent_words = words_info (full_path)
print (Most_frequent_words)

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
wordcloud.to_file(output_wordcloud_path)

print(f"Word cloud saved to {output_wordcloud_path}")

