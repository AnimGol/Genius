import os

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
            second_lexicon[word] = f"{count}, {emotions}"  # Store count and emotions as a string
    return second_lexicon

        
text_result = analysis (full_path)
print (text_result)
