# Import necessary modules and classes
import emotion_analysis
from datetime import datetime, timedelta
from fastapi.responses import FileResponse
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
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
import uvicorn
import csv

# To import emotion_analysis in this main_ted file
from fastapi import APIRouter


# Initialize the FastAPI app
app = FastAPI()

# Serve the static folder (for favicon.ico)
app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.get("/favicon.ico")
# async def favicon():
#         return FileResponse("static/favicon.ico")

###################################
#       EMOTIONAL ANALYSIS        #
###################################

# 1) Show a simple form for the user to input the text_id
@app.get("/analysis-form", response_class=HTMLResponse)
async def analysis_form(request: Request):
    user = request.session.get("user")  # Check if user is logged in
    if not user:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse("analysis_form.html", {"request": request})  # Show the form

# 2
@app.get("/analysis-menu", response_class=HTMLResponse)
async def show_analysis_menu(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    # ✅ Call `main_menu()` to display menu options
    menu_text = emotion_analysis.main_menu()  # This should return a menu prompt

    return templates.TemplateResponse("analysis_menu.html", {"request": request, "menu_text": menu_text})


@app.post("/select-analysis-option", response_class=HTMLResponse)
async def process_menu_option(request: Request, option: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    if option == "1":
        return templates.TemplateResponse("enter_text_id.html", {"request": request})
    elif option == "2":
        return RedirectResponse("/find-emotions", status_code=302)
    elif option == "3":
        return RedirectResponse("/logout", status_code=302)
    else:
        return JSONResponse(content={"message": "Invalid option, please enter a valid choice."})


@app.post("/start-analysis", response_class=HTMLResponse)
async def perform_analysis(request: Request, text_id: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    # 1) Call the updated function from emotion_analysis
    try:
        # This now returns a dictionary (analysis_summary)
        analysis_dict = emotion_analysis.perform_text_analysis(text_id, CLI=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 2) Convert the results to JSON (or a simple string) for storage
    import json
    analysis_results_json = json.dumps(analysis_dict)  

    # 3) Find the current user's user_id
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE username = ?", (user,))
    user_data = cursor.fetchone()
    if not user_data:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found in DB.")
    user_id = user_data[0]

    # 4) Insert a new row into uploaded_texts to save the analysis
    cursor.execute("""
        INSERT INTO uploaded_texts (user_id, content, analysis_results)
        VALUES (?, ?, ?)
    """, (user_id, text_id, analysis_results_json))

    conn.commit()
    conn.close()

    # 5) Return a template with the analysis results
    return templates.TemplateResponse(
        "analysis_result.html",
        {"request": request, "analysis": analysis_dict}
    )



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



@app.get("/my-analyses", response_class=HTMLResponse)
async def my_analyses(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Get user_id
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (user,))
    user_data = cursor.fetchone()
    if not user_data:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found in the .")
    user_id = user_data[0]

    # Fetch the rows for this user
    cursor.execute("SELECT upload_id, content, analysis_results FROM uploaded_texts WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    # Convert them to a structure you can use in a template
    # Or just return as JSON for testing
    return templates.TemplateResponse(
        "my_analyses.html",
        {"request": request, "analyses": rows}
    )

@app.get("/all-analyses", response_class=HTMLResponse)
async def get_all_analyses(request: Request):
    current_user = request.session.get("user")
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    # Check admin
    if not is_admin(current_user):
        # If user is not admin, redirect or raise an error
        return RedirectResponse("/dashboard", status_code=302)

    # If admin, fetch all analyses from all users
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            uploaded_texts.upload_id,
            users.username,
            uploaded_texts.content AS text_id,
            uploaded_texts.analysis_results
        FROM uploaded_texts
        JOIN users ON uploaded_texts.user_id = users.user_id
    """)
    rows = cursor.fetchall()
    conn.close()

    # Render them in a new template
    return templates.TemplateResponse(
        "all_analyses.html",
        {"request": request, "rows": rows}
    )

@app.get("/find-emotions", response_class=HTMLResponse)
async def find_emotions_form(request: Request):
    """
    Show a form to allow the user to input an emotion and a threshold.
    """
    user = request.session.get("user")  # Check if user is logged in
    if not user:
        return RedirectResponse("/login", status_code=302)

    # Render a simple form asking for emotion and threshold
    return templates.TemplateResponse(
        "find_emotions_form.html",
        {"request": request}
    )


@app.post("/find-emotions", response_class=HTMLResponse)
async def process_find_emotions(
    request: Request,
    emotion: str = Form(...),
    threshold: float = Form(...)
):
    """
    Process the form data, scan the .tsv files in the 'results' folder,
    and look for any file where the given emotion has a percentage higher
    than the provided threshold.
    """
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    # Directory where your emotion_percentage_*.tsv files are saved
    results_folder = "results"
    matching_files = []

    # Scan through each file looking for the specified emotion with percentage > threshold
    for filename in os.listdir(results_folder):
        if filename.startswith("emotion_percentage_") and filename.endswith(".tsv"):
            file_path = os.path.join(results_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter='\t')
                next(reader)  # skip header: Emotion, Count, Percentage

                for row in reader:
                    if len(row) < 3:
                        continue

                    row_emotion, row_count, row_percentage = row
                    if row_emotion.lower() == emotion.lower():
                        try:
                            if float(row_percentage) > threshold:
                                matching_files.append(filename)
                                break  # Stop scanning this file, move to next
                        except ValueError:
                            # If row_percentage isn't convertible to float
                            pass

    # Render a results page
    return templates.TemplateResponse(
        "find_emotions_results.html",
        {
            "request": request,
            "emotion": emotion,
            "threshold": threshold,
            "matching_files": matching_files
        }
    )

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

def is_admin(username: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0] == 'admin':
        return True
    return False

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
async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
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

    # Check the  from DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ?", (user,))
    result = cursor.fetchone()
    conn.close()

    user_role = result[0] if result else "user"

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "role": user_role
        }
    )

@app.get("/users-list", response_class=HTMLResponse)
async def show_users_list(request: Request):
    current_user = request.session.get("user")
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    # Check if admin
    if not is_admin(current_user):
        return RedirectResponse("/dashboard", status_code=302)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, role FROM users")
    users_rows = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse(
        "users_list.html",
        {"request": request, "users": users_rows}
    )

# Dictionary to store active sessions
sessions = {}
TIMEOUT_MINUTES = 3  # 3-minute timeout

def get_current_user(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token or session_token not in sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    session_info = sessions[session_token]
    if datetime.utcnow() - session_info["last_active"] > timedelta(minutes=TIMEOUT_MINUTES):
        del sessions[session_token]  # Remove session on timeout
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired. Please log in again.")
    
    # Update last active time
    sessions[session_token]["last_active"] = datetime.utcnow()
    return session_info["user"]

@app.post("/login")
def login(response: Response, username: str):
    session_token = f"token_{username}"  # Simple token generation (should use a secure method)
    sessions[session_token] = {"user": username, "last_active": datetime.utcnow()}
    response.set_cookie(key="session_token", value=session_token)
    return {"message": "Login successful", "session_token": session_token}

# Logout and thank-you page
@app.get("/logout")
def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token and session_token in sessions:
        del sessions[session_token]
        response.delete_cookie("session_token")
    return JSONResponse(content={"message": "Thank you for using our program! You have been logged out."})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...)          # <-- NEW
):
    print("Form data received:", name, username, password, role)  # Debugging line
    hashed_password = pwd_context.hash(password)  # Hash the password before storing

    # Validate the role to ensure it’s either 'user' or 'admin'
    if role not in ("user", "admin"):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "message": "Invalid role selection."}
        )

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "message": "Username already exists"}
            )

        # Insert the new user with the chosen role
        cursor.execute(
            "INSERT INTO users (name, username, hashed_password, role) VALUES (?, ?, ?, ?)",
            (name, username, hashed_password, role)
        )
        conn.commit()
        conn.close()

        return templates.TemplateResponse(
            "register.html",
            {"request": request, "message": "User registered successfully!"}
        )

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "message": "Database error occurred"}
        )
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
