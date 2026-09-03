import sqlite3
import os
import sys

# Ensure parent directory is in sys.path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

DB_NAME = "hospital.db"


def get_db_path():
    # Keep DB file in root workspace directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, DB_NAME)

def get_connection():
    """Returns a SQLite connection with row_factory set to sqlite3.Row and foreign keys enabled."""
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
