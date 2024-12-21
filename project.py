import sqlite3
#  connecting to our database 
conn = sqlite3.connect(r'C:\Users\minag\OneDrive\Desktop\project\Genius.db')
# Create a cursor object to interact with the database
cursor = conn.cursor()



# Enable foreign key constraints
cursor.execute("PRAGMA foreign_keys = ON")


# book_id is in TEXT format to allow special characters for users unique manually uploaded texts. 
cursor.execute( 
    """CREATE TABLE IF NOT EXISTS books (
        book_id TEXT PRIMARY KEY, 
        title TEXT NOT NULL,
        author TEXT,
        Translator TEXT, 
        Genre TEXT,
        Publication_year INTEGER,
        Publisher TEXT,
        Language TEXT,
        content TEXT NOT NULL
    )""")

cursor.execute(
    """CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
    )""")

cursor.execute(
    """CREATE TABLE uploaded_texts (
        upload_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        analysis_results TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )""")





# Commit and close the connection
conn.commit()
conn.close()