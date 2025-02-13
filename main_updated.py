# Import necessary modules and classes
import emotion_analysis
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
#from uuid import UUID, uuid4
from pydantic import BaseModel
from enum import Enum
from passlib.context import CryptContext
#import models
#from database import engine, SessionLocal
#from sqlalchemy.orm import Session
import sqlite3
from sqlite3 import Error
import os

# To import emotion_analysis in this main_ted file
from fastapi import APIRouter


# Initialize the FastAPI app
app = FastAPI()

# Serve the static folder (for favicon.ico)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

router = APIRouter() # From here downwards, I've imported emotion_analysis to this "main_ted" file.

@router.get("/emotion-analysis/{text_id}")
async def run_emotion_analysis(text_id: str):
    try:
        file_path = f"SPGC-counts-2018-07-18/PG{text_id}_counts.txt"
        print(f"Looking for file at: {os.path.abspath(file_path)}")  # Debugging line
        # Call the analysis function from emotion_analysis.py
        result = emotion_analysis.analysis(f"SPGC-counts-2018-07-18/PG{text_id}_counts.txt")
        #result = emotion_analysis.analysis(file_path)
        return {"text_id": text_id, "analysis": result}

    except FileNotFoundError:
        #raise HTTPException(status_code=404, detail="File not found")
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")  # Show missing file name

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router) # This is the last line of code to import emtion_analysis in this main_ted file.


#models.base.metadata.create_all(bind=engine) # It will create a DB and table if they don't already exist.

#def get_db(): # Here we'll create a SessionLocal which in turns create our Db instance and then we'll also close the Db instance.
#    try:
#        db = SessionLocal()
#        yield db
#    finally:
#        db.close() # Now, we'll gonna use Dependency Injection Platform on FastAPI. So, eveytime this function gets called, we want to automatically open a Db Session and automatically close it. So, in 1st line of code we add 'Depends'.
# And now in all of the parameters we'll call the Dependency injection.
# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# Set up templates
templates = Jinja2Templates(directory="templates")

# In-memory user database (for demonstration purposes)
users_db = {}

# Database connection setup
DB_PATH = os.path.abspath("Genius.db")
print("Database path:", DB_PATH)

# Initialize the SQLite database
def initialize_db():
    conn = sqlite3.connect(DB_PATH)   # Connect to the SQLite database file (creates it if it doesn't exist)
    cursor = conn.cursor()            # Create a cursor object to execute SQL commands

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")

    # Create tables, cursor.execute() executes SQL commands. Here, it creates a table named books with columns book_id, title, and so on.
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
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS uploaded_texts (
            upload_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            analysis_results TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )"""
    )

    conn.commit() # Commit the changes
    conn.close()  # Close the connection


try:
    # Connect with timeout and enable row factory
    connection = sqlite3.connect(
        'Genius.db',
        timeout=10,
        detect_types=sqlite3.PARSE_DECLTYPES,
        isolation_level='EXCLUSIVE'
    )
    connection.row_factory = sqlite3.Row
    print("Advanced connection established!")

except Error as e:
    print(f"Error occurred: {e}")

finally:
    if connection:
        connection.close()

# Initialize the database when the app starts
initialize_db()
# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Roles
class Role(str, Enum):
#   id: Optional [UUID] = uuid4
    admin: "admin"
    user: "user"
    student: "student"

# Models
class User(BaseModel):
#   id: Optional [UUID] = uuid4()
    username: str
    password: str
    roles: List[Role]

# Routes

# Login page (GET request)
@app.get("/login", response_class=HTMLResponse) # "/login" is a path parameter
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request}) # In curly brackets "request" is the key and request is the value.


@app.post("/login")
async def login_user(I: Request, username: str = Form(...), password: str = Form(...)):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Retrieve the hashed password from the database
        cursor.execute("SELECT hashed_password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        # Check if user exists and verify password
        if not user or not pwd_context.verify(password, user[0]):  # Compare hashed password
            raise HTTPException(status_code=401, detail="Invalid username or password - test")

        # Save user session (if using sessions, ensure session middleware is configured)
        request.session["user"] = username
        return RedirectResponse("/dashboard", status_code=302)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")

# Dashboard page
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


# Logout and thank-you page
@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()
    return templates.TemplateResponse("thank_you.html",
                                      {"request": request, "message": "Thank you for using the system!"})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register_user(
        name: str = Form(...),
        username: str = Form(...),
        password: str = Form(...)
):
    hashed_password = pwd_context.hash(password)  # Hash the password before storing

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Username already exists")

        # Insert the new user with default role = 'user'
        cursor.execute(
            "INSERT INTO users (name, username, hashed_password, role) VALUES (?, ?, ?, ?)",
            (name, username, hashed_password, "user")
        )
        conn.commit()
        conn.close()

        return {"message": "User registered successfully"}

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")

""
# User Registration
@app.post("/register")
#async def register_user(user: User):
async def register_user_new(user: User):  # Change the function name
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, hashed_password, role) VALUES (?, ?, 'user')",
                   (user.username, user.password))
    conn.commit()
    conn.close()
    return {"message": "User registered successfully"}
""
# PUT Methods for updating users and books
@app.put("/users/{user_id}")
async def update_user(user_id: int, name: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        updates = []
        values = []
        if name:
            updates.append("name = ?")
            values.append(name)
        if password:
            hashed_password = pwd_context.hash(password)
            updates.append("hashed_password = ?")
            values.append(hashed_password)

        if updates:
            values.append(user_id)
            cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?", values)
            conn.commit()
        conn.close()
        return {"message": "User updated successfully"}
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@app.put("/books/{book_id}")
async def update_book(book_id: str, title: Optional[str] = Form(None), author: Optional[str] = Form(None)):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        updates = []
        values = []
        if title:
            updates.append("title = ?")
            values.append(title)
        if author:
            updates.append("author = ?")
            values.append(author)

        if updates:
            values.append(book_id)
            cursor.execute(f"UPDATE books SET {', '.join(updates)} WHERE book_id = ?", values)
            conn.commit()
        conn.close()
        return {"message": "Book updated successfully"}
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")

# DELETE Methods for deleting users and books
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return {"message": "User deleted successfully"}
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@app.delete("/books/{book_id}")
async def delete_book(book_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
        conn.commit()
        conn.close()
        return {"message": "Book deleted successfully"}
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")

# Example route to verify the database connection
#@app.get("/books")
#async def get_books():
#    conn = sqlite3.connect(DB_PATH)
#    cursor = conn.cursor()
#    cursor.execute("SELECT * FROM books")
#    books = cursor.fetchall()
#    conn.close()
#    return {"books": books}

@app.get("/books", response_model=list)
async def get_books():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT book_id, title, author FROM books")  # Select specific columns
        books = cursor.fetchall()
        conn.close()

        # Convert the result into a list of dictionaries
        books_list = [{"book_id": row[0], "title": row[1], "author": row[2]} for row in books]
        return {"books": books_list}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
        #return {"error": str(e)}



# Test database connection
@app.get("/test-db")
async def test_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        return {"message": "Database connected successfully!", "tables": tables}
    except Exception as e:
        return {"error": str(e)}