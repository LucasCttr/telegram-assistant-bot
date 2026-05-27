import sqlite3
from datetime import datetime
import os

MODULE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(MODULE_DIR, "bot_images.db")

def initialize_db():
    """Creates the database file and the images table if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_path TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_image(user_id: int, image_path: str):
    """Saves a new image record sent by the user."""
    initialize_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO images (user_id, image_path, created_at) VALUES (?, ?, ?)",
        (user_id, image_path, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_latest_images(user_id: int, limit: int = 2):
    """Returns the latest image paths for a specific user (defaults to the last 2)."""
    initialize_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT image_path FROM images WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    # Returns a clean list of strings containing the paths
    return [row[0] for row in rows]