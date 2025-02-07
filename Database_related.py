import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("Genius.db") 
cursor = conn.cursor()

# cursor.execute('''ALTER TABLE "Works Collection" ADD COLUMN "wordcloud for Most Frequent Words" TEXT''')
# cursor.execute('''ALTER TABLE "Works Collection" ADD COLUMN "wordcloud for nonstop words" TEXT''')
# cursor.execute('''ALTER TABLE "Works Collection" ADD COLUMN "Barchart for emotion analysis" TEXT''')


# Check if the table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Works Collection'")
table_exists = cursor.fetchone()

if table_exists:
    print("Table exists!")
    
    # Check and print the structure of the table
    cursor.execute('PRAGMA table_info("Works Collection")')
    columns = cursor.fetchall()
    
    if columns:
        print("Columns in 'Works Collection':")
        for column in columns:
            print(column)  # Prints column details
    else:
        print("No columns found in the table.")
else:
    print("Table does NOT exist.")

# Close the connection
conn.close()
