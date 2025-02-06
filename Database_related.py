import sqlite3


conn = sqlite3.connect(r"Genius.db") 
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Works Collection'")
table_exists = cursor.fetchone()

if table_exists:
    print("Table exists!")
    cursor.execute('PRAGMA table_info("Works Collection")')
    columns = cursor.fetchall()
    if columns:
        for column in columns:
            print(column)
    else:
        print("No columns found in the table.")
else:
    print("Table does NOT exist.")

# Check the structure of the Works Collection table
cursor.execute('PRAGMA table_info("Works Collection")')
columns = cursor.fetchall()

# Print column names and types
for column in columns:
    print(column)


conn.close()
