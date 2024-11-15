# user_service.py
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this if UI is running on a different port
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


BOOK_SERVICE_URL = "http://localhost:8002"

# Define the data model for a User
class User(BaseModel):
    username: str
    email: str
    password: str

# Connect to the database (SQLite)
def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create the users table (if it doesn't exist)
def create_users_table():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    );
    ''')
    conn.commit()
    conn.close()

create_users_table()

# Register a new user
@app.post("/users/")
def create_user(user: User):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO users (username, email, password)
    VALUES (?, ?, ?);
    ''', (user.username, user.email, user.password))
    conn.commit()
    conn.close()
    return {"message": "User created successfully"}

# Get user details by ID
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(username=user['username'], email=user['email'], password=user['password'])
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users/{user_id}/check_availability/{book_id}")
async def check_availability(user_id: int, book_id: int):
    # Call the Book Service to check if the book is available
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BOOK_SERVICE_URL}/books/{book_id}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book = response.json()
    if not book["available"]:
        return {"message": f"Book with title {book['title']} and id {book_id} is not available"}
    
    # Here, add code to handle borrowing the book in User Service
    return {"message": f"Book with title {book['title']} and id {book_id} is available"}