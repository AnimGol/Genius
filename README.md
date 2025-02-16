# Text Analysis Program - README

## Introduction: What does the program do?

This program is designed for researchers, linguists, or anyone interested in text analysis. It analyze texts for emotional content and word frequency and provide the results in visualized formats. It can also search in the texts to find out in which texts a particular emotion appeared more than a specific percentage.

Here are some of the features of this program:
- In this program, Standardized Gutenberg Project Corpus (SGPC) was used to collect necessary files in our database named "Genius" which is a SQLite relational database and is used to analyze different texts provided there. 
- The program uses GUI (FastAPI) and contains a user-management system. After a successful login, users can use the program and see the analysis.
- The program uses the NRC Emotion Lexicon to analyze emotions. 




## Requirements
- Python 3.12
- The files on the "Genius" repository on Github (including "SPGC-counts-2018-07-18", "styles.css" located in the "static" folder, "Genius.db", "NRC-Emotion-Lexicon-Wordlevel-v0.92.txt", "main_updated.py" and "emotion_analysis.py")
- External Libraries:
   SpaCy
   uvicorn
   fastapi
   itsdangerous
   passlib
   pythn-multipart
   bcrypt


- Recommended IDE: ?




### Installation Instructions
1. Install Python 3.12 if it is not already installed, from the official Python website: python.org.
2. Install the required libraries using pip. (Run "pip install spacy uvicorn fastapi itsdangerous passlib python-multipart bcrypt" on your terminal or Command Prompt)
3. Download the en_core_web_lg model for SpaCy: python -m spacy download en_core_web_lg
4. Clone the repository to your pc.


## How to Run the Program
1. Open the cmd (or equivalent) and clone the "Genius" repository to your pc: git clone https://github.com/{yourusername}/Genius.git
2. Navigate to your cloned repository in your pc.
3. Install the required libraries, mentioned above.
4. Run this command: uvicorn main_updated:app --reload.
5. Open the URL link provided there (Usually http://127.0.0.1:8000)and add "/register#/" to the end of the link.



## Output
The program creates the following output files:
- Lemmatized version of the file (name format: PG{text id number}_counts_lemmatized.txt, ex. PG2_counts_lemmatized.txt): This file includes 2 columns. The first column contains the lemmas and the second one the count of the related lemma. This file is saved in the folder of "SPGC-counts-2018-07-18".
- (name format: emotion_analysis_{text id number}.tsv, ex. emotion_analysis_2.tsv): This file has 3 columns, including lemmas (although the header is "word"), counts and emotions respectively. This file is saved in the "result" folder.
- (name format: emotion_percentage_{text id number}.tsv, ex. emotion_percentage_2.tsv): This file also has 3 columns including emotions, their counts and their percentages respectively. This file is saved in the "result" folder.
- Bar chart for emotions (name format: barchart{text id number}.png, ex.barchart2.png): This barchart depicts the frequency of each emotion. It is saved in the "result" folder.
- wordcloud of the 50 most frequent words (name format: wordcloud_{text id number}.png, ex. wordcloud_2.png): saved in the "result" folder.
- wordcloud for most frequent non-stop words (name format: wordcloud_nonstop_{text id number}.png, ex. wordcloud_nonstop_2.png): This wordcloud depicts up to 10 words which were used most frequently. This word cloud is extracted from the aforementioned word cloud for the 50 most frequent words. It is saved in the "result" folder. 
- Total Word count in the text. It is written in the terminal (ex. "Word count in this text is  725973").


## Program Description
- ** ? **



## Contact Information
For any questions or support, please contact the following emails:
minagol91@gmail.com
or
qasimhabib.314@gmail.com
or
alihmohammad3334@gmail.com

