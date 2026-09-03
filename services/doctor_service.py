from database.db import get_connection
from utils.validators import validate_email, validate_phone, validate_non_negative

SPECIALIZATIONS = [
    "General Physician",
    "Cardiologist",
    "Dermatologist",
    "Neurologist",
    "Orthopedic",
    "Pediatrician",
    "Gynecologist",
    "ENT Specialist",
    "Dentist",
    "Ophthalmologist",
    "Psychiatrist"
]

def add_doctor(data: dict) -> tuple[int | None, str]:
    """Adds a new doctor record."""
    full_name = data.get("full_name", "").strip()
    specialization = data.get("specialization", "").strip()
    qualification = data.get("qualification", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    experience_years = data.get("experience_years", 0)
    consultation_fee = data.get("consultation_fee", 0.0)
    available_days = data.get("available_days", "").strip()
    start_time = data.get("start_time", "").strip()
    end_time = data.get("end_time", "").strip()
    slot_duration = data.get("slot_duration", 30)
    room_number = data.get("room_number", "").strip()
    status = data.get("status", "Active")

    if not full_name:
        return None, "Full name is required."
    if not specialization:
        return None, "Specialization is required."
    if not validate_phone(phone):
        return None, "Invalid phone number."
    if not validate_email(email):
        return None, "Invalid email address."
        
    valid_fee, fee_err = validate_non_negative(consultation_fee, "Consultation fee")
    if not valid_fee:
        return None, fee_err
        
    if not available_days:
        return None, "Available days must be specified."
    if not start_time or not end_time:
        return None, "Start and end times are required."
    if start_time >= end_time:
        return None, "Start time must be earlier than end time."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO doctors (full_name, specialization, qualification, phone, email, experience_years, consultation_fee, available_days, start_time, end_time, slot_duration, room_number, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (full_name, specialization, qualification, phone, email, experience_years, consultation_fee, available_days, start_time, end_time, slot_duration, room_number, status))
        doctor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doctor_id, ""
    except Exception as e:
        conn.close()
        return None, f"Database error adding doctor: {str(e)}"

def get_all_doctors(search_term: str = "", spec_filter: str = "All", status_filter: str = "All") -> list[dict]:
    """Retrieves all doctors with filtering options."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM doctors WHERE 1=1"
    params = []

    if search_term:
        query += " AND (full_name LIKE ? OR qualification LIKE ? OR room_number LIKE ?)"
        term = f"%{search_term.strip()}%"
        params.extend([term, term, term])

    if spec_filter != "All":
        query += " AND specialization = ?"
        params.append(spec_filter)

    if status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY doctor_id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def get_doctor_by_id(doctor_id: int) -> dict | None:
    """Gets doctor record by doctor_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_doctor(doctor_id: int, data: dict) -> tuple[bool, str]:
    """Updates an existing doctor record."""
    full_name = data.get("full_name", "").strip()
    specialization = data.get("specialization", "").strip()
    qualification = data.get("qualification", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    experience_years = data.get("experience_years", 0)
    consultation_fee = data.get("consultation_fee", 0.0)
    available_days = data.get("available_days", "").strip()
    start_time = data.get("start_time", "").strip()
    end_time = data.get("end_time", "").strip()
    slot_duration = data.get("slot_duration", 30)
    room_number = data.get("room_number", "").strip()
    status = data.get("status", "Active")

    if not full_name:
        return False, "Full name is required."
    if not validate_phone(phone):
        return False, "Invalid phone number."
    if not validate_email(email):
        return False, "Invalid email address."
    valid_fee, fee_err = validate_non_negative(consultation_fee, "Consultation fee")
    if not valid_fee:
        return False, fee_err
    if start_time >= end_time:
        return False, "Start time must be before end time."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE doctors
            SET full_name = ?, specialization = ?, qualification = ?, phone = ?, email = ?,
                experience_years = ?, consultation_fee = ?, available_days = ?, start_time = ?,
                end_time = ?, slot_duration = ?, room_number = ?, status = ?
            WHERE doctor_id = ?
        """, (full_name, specialization, qualification, phone, email, experience_years, consultation_fee, available_days, start_time, end_time, slot_duration, room_number, status, doctor_id))
        conn.commit()
        conn.close()
        return True, "Doctor details updated successfully!"
    except Exception as e:
        conn.close()
        return False, f"Database error updating doctor: {str(e)}"

def delete_doctor(doctor_id: int) -> tuple[bool, str]:
    """Deletes a doctor record along with related appointments and bills."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM bills WHERE appointment_id IN (SELECT appointment_id FROM appointments WHERE doctor_id = ?)", (doctor_id,))
        cursor.execute("DELETE FROM appointments WHERE doctor_id = ?", (doctor_id,))
        cursor.execute("DELETE FROM doctors WHERE doctor_id = ?", (doctor_id,))
        conn.commit()
        conn.close()
        return True, "Doctor and associated appointment records deleted successfully!"
    except Exception as e:
        conn.close()
        return False, f"Database error deleting doctor: {str(e)}"

