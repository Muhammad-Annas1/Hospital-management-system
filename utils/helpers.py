import hashlib

def hash_password(password: str) -> str:
    """Hashes a password using SHA-256 with a fixed salt."""
    salt = "hospital_system_salt_2026"
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies password match."""
    return hash_password(password) == hashed_password

def format_currency(amount: float) -> str:
    """Formats numeric amount into PKR currency format (e.g. Rs. 2,000)."""
    return f"Rs. {amount:,.0f}"


def get_status_color(status: str) -> str:
    """Returns CSS color hex or badge class for status display."""
    status_lower = str(status).lower()
    mapping = {
        'pending': '#f59e0b',     # Amber / Yellow
        'confirmed': '#3b82f6',   # Blue
        'completed': '#10b981',   # Green
        'cancelled': '#ef4444',   # Red
        'paid': '#10b981',        # Green
        'partially paid': '#8b5cf6', # Purple
        'active': '#10b981',      # Green
        'inactive': '#6b7280'     # Gray
    }
    return mapping.get(status_lower, '#6b7280')

def render_badge(status: str) -> str:
    """Returns HTML for a styled status badge."""
    color = get_status_color(status)
    return f'<span style="background-color: {color}22; color: {color}; border: 1px solid {color}; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85rem;">{status}</span>'
