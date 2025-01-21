import sqlite3
import os
import time

# Set paths
txt_folder_path = r"C:\Users\minag\Genius\SPGC-counts-2018-07-18"
db_path = r"C:\Users\minag\Genius\Genius.db"

# Start the timer
start_time = time.time()

print("Starting script...")

# Connect to the SQLite database with a timeout of 10 seconds to avoid locking issues
conn = sqlite3.connect(db_path, timeout=10)
cursor = conn.cursor()

# Enable Write-Ahead Logging for better concurrency
cursor.execute("PRAGMA journal_mode=WAL;")

# Read files from the folder and update the database
print("Reading files from the folder...")
for idx, filename in enumerate(os.listdir(txt_folder_path)):
    if filename.endswith("_counts.txt"):
        print(f"Processing file {idx + 1}/{len(os.listdir(txt_folder_path))}: {filename}")
        
        # Extract book_id from filename (e.g., PG10_counts -> PG10)
        book_id = filename.split("_")[0]
        file_path = os.path.join(txt_folder_path, filename)

        # Try to update the database for the current file
        try:
            print(f"Attempting to update the database for book ID: {book_id}")
            cursor.execute("""
                UPDATE "Works Collection"
                SET Counts = ?
                WHERE id = ?;
            """, (file_path, book_id))
            print(f"Successfully updated for book ID: {book_id}")
        except sqlite3.OperationalError as e:
            print(f"Error updating for {filename}: {e}")
        except Exception as e:
            print(f"Unexpected error for {filename}: {e}")
    
    # Log progress every 1000 files
    if idx % 1000 == 0:
        print(f"Processed {idx} files so far...")

# Commit changes to the database
print("Committing changes to the database...")
conn.commit()

# Close the database connection
conn.close()

# End the timer and print the duration
print(f"Script completed in {time.time() - start_time:.2f} seconds.")
