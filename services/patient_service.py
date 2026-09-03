import json
import os
from database.db import get_connection
from utils.validators import validate_email, validate_phone, validate_dob, calculate_age
from datetime import datetime, date

JSON_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "registered_patients.json")

def sync_patients_json():
    """Syncs all patient records and usernames from SQLite to a readable JSON file."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, u.username
        FROM patients p
        LEFT JOIN users u ON p.patient_id = u.patient_id
        ORDER BY p.patient_id ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    patients_list = []
    for row in rows:
        p_dict = dict(row)
        patients_list.append({
            "patient_id": p_dict.get("patient_id"),
            "full_name": p_dict.get("full_name"),
            "username": p_dict.get("username", "N/A"),
            "gender": p_dict.get("gender"),
            "date_of_birth": p_dict.get("date_of_birth"),
            "age": p_dict.get("age"),
            "phone": p_dict.get("phone"),
            "email": p_dict.get("email"),
            "address": p_dict.get("address"),
            "blood_group": p_dict.get("blood_group"),
            "disease_problem": p_dict.get("disease_problem"),
            "emergency_contact": p_dict.get("emergency_contact"),
            "registration_date": p_dict.get("registration_date"),
            "registration_time": p_dict.get("registration_time", "09:00 AM"),
            "status": p_dict.get("status")
        })

    try:
        with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(patients_list, f, indent=4)
    except Exception as e:
        print(f"Error writing to {JSON_FILE_PATH}: {e}")

def add_patient(data: dict) -> tuple[int | None, str]:
    """Validates and adds a new patient record."""
    full_name = data.get("full_name", "").strip()
    gender = data.get("gender", "").strip()
    dob = data.get("date_of_birth")
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    address = data.get("address", "").strip()
    blood_group = data.get("blood_group", "").strip()
    disease_problem = data.get("disease_problem", "").strip()
    emergency_contact = data.get("emergency_contact", "").strip()
    status = data.get("status", "Active")

    if not full_name:
        return None, "Full name is required."
    if not gender:
        return None, "Gender is required."
    
    valid_dob, dob_err = validate_dob(dob)
    if not valid_dob:
        return None, dob_err
        
    if not validate_phone(phone):
        return None, "Invalid phone number format."
    if not validate_email(email):
        return None, "Invalid email address format."

    dob_str = str(dob)
    age = calculate_age(dob)
    now = datetime.now()
    reg_date = now.strftime("%Y-%m-%d")
    reg_time = now.strftime("%I:%M %p")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO patients (full_name, gender, date_of_birth, age, phone, email, address, blood_group, disease_problem, emergency_contact, registration_date, registration_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (full_name, gender, dob_str, age, phone, email, address, blood_group, disease_problem, emergency_contact, reg_date, reg_time, status))
        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Sync to readable registered_patients.json file
        sync_patients_json()
        return patient_id, ""
    except Exception as e:
        conn.close()
        return None, f"Database error adding patient: {str(e)}"

def get_all_patients(search_term: str = "", gender_filter: str = "All", status_filter: str = "All") -> list[dict]:
    """Retrieves all patients with optional search and filter options."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM patients WHERE 1=1"
    params = []

    if search_term:
        query += " AND (full_name LIKE ? OR phone LIKE ? OR email LIKE ?)"
        term = f"%{search_term.strip()}%"
        params.extend([term, term, term])

    if gender_filter != "All":
        query += " AND gender = ?"
        params.append(gender_filter)

    if status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY patient_id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def get_patient_by_id(patient_id: int) -> dict | None:
    """Gets patient record by patient_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_patient(patient_id: int, data: dict) -> tuple[bool, str]:
    """Updates an existing patient record."""
    full_name = data.get("full_name", "").strip()
    gender = data.get("gender", "").strip()
    dob = data.get("date_of_birth")
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    address = data.get("address", "").strip()
    blood_group = data.get("blood_group", "").strip()
    disease_problem = data.get("disease_problem", "").strip()
    emergency_contact = data.get("emergency_contact", "").strip()
    status = data.get("status", "Active")

    if not full_name:
        return False, "Full name is required."
    valid_dob, dob_err = validate_dob(dob)
    if not valid_dob:
        return False, dob_err
    if not validate_phone(phone):
        return False, "Invalid phone number."
    if not validate_email(email):
        return False, "Invalid email address."

    dob_str = str(dob)
    age = calculate_age(dob)

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE patients
            SET full_name = ?, gender = ?, date_of_birth = ?, age = ?, phone = ?, email = ?,
                address = ?, blood_group = ?, disease_problem = ?, emergency_contact = ?, status = ?
            WHERE patient_id = ?
        """, (full_name, gender, dob_str, age, phone, email, address, blood_group, disease_problem, emergency_contact, status, patient_id))
        conn.commit()
        conn.close()
        
        sync_patients_json()
        return True, "Patient updated successfully!"
    except Exception as e:
        conn.close()
        return False, f"Database error updating patient: {str(e)}"

def delete_patient(patient_id: int) -> tuple[bool, str]:
    """Deletes a patient record along with their user login, appointments, and bills."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM bills WHERE patient_id = ?", (patient_id,))
        cursor.execute("DELETE FROM appointments WHERE patient_id = ?", (patient_id,))
        cursor.execute("DELETE FROM users WHERE patient_id = ?", (patient_id,))
        cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
        conn.commit()
        conn.close()
        
        sync_patients_json()
        return True, "Patient and all related records deleted successfully!"
    except Exception as e:
        conn.close()
        return False, f"Database error deleting patient: {str(e)}"
