import sqlite3

conn = sqlite3.connect(r"C:\Users\minag\Genius\Genius.db")

cursor = conn.cursor()


# Add the first column
cursor.execute("ALTER TABLE 'Works Collection' ADD COLUMN 'wordcloud for Most Frequent Words' BLOB")

# Add the second column
cursor.execute("ALTER TABLE 'Works Collection' ADD COLUMN 'wordcloud for nonstop words' BLOB")

# Add the third column
cursor.execute("ALTER TABLE 'Works Collection' ADD COLUMN 'Barchart for emotion analysis' BLOB")

conn.commit ()
conn.close()