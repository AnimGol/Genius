import sqlite3


conn = sqlite3.connect(r"C:\Users\minag\Genius\Genius.db") 
cursor = conn.cursor()

# Check the structure of the Works Collection table
cursor.execute("PRAGMA table_info(Works Collection)")
columns = cursor.fetchall()

# Print column names and types
for column in columns:
    print(column)


conn.close()
