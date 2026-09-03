from database.db import get_connection
from utils.helpers import hash_password, verify_password

def authenticate_user(username: str, password: str) -> tuple[dict | None, str]:
    """
    Authenticates user credentials.
    Returns (user_dict, error_message).
    """
    if not username or not password:
        return None, "Username and password are required."

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username.strip(),))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None, "Invalid username or password."

    user_dict = dict(row)
    if not verify_password(password, user_dict["password_hash"]):
        return None, "Invalid username or password."

    return user_dict, ""

def create_user(username: str, password: str, role: str, patient_id: int | None = None) -> tuple[bool, str]:
    """Creates a new user login account."""
    if not username or len(username.strip()) < 3:
        return False, "Username must be at least 3 characters long."
    if not password or len(password) < 4:
        return False, "Password must be at least 4 characters long."

    conn = get_connection()
    cursor = conn.cursor()

    # Check if username exists
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (username.strip(),))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists. Please choose a different username."

    hashed = hash_password(password)
    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, patient_id)
            VALUES (?, ?, ?, ?)
        """, (username.strip(), hashed, role, patient_id))
        conn.commit()
        conn.close()

        # Update JSON file
        try:
            from services.patient_service import sync_patients_json
            sync_patients_json()
        except Exception:
            pass

        return True, "Account created successfully!"
    except Exception as e:
        conn.close()
        return False, f"Database error creating user: {str(e)}"

