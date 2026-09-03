from database.db import get_connection
from utils.appointment_utils import get_available_slots_for_doctor, is_doctor_available_on_date
from datetime import datetime, date

def get_booked_slots(doctor_id: int, appointment_date: str) -> list[str]:
    """Returns list of HH:MM strings already booked for doctor on appointment_date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT appointment_time FROM appointments
        WHERE doctor_id = ? AND appointment_date = ? AND status != 'Cancelled'
    """, (doctor_id, appointment_date))
    rows = cursor.fetchall()
    conn.close()
    return [row["appointment_time"] for row in rows]

def get_available_slots_for_booking(doctor_id: int, booking_date: date | str) -> tuple[list[str], str]:
    """Helper to retrieve available time slots for a given doctor and date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,))
    doc_row = cursor.fetchone()
    conn.close()

    if not doc_row:
        return [], "Doctor not found."

    doctor_info = dict(doc_row)
    if doctor_info["status"] != "Active":
        return [], "This doctor is currently inactive."

    date_str = str(booking_date)
    booked_times = get_booked_slots(doctor_id, date_str)
    return get_available_slots_for_doctor(doctor_info, booking_date, booked_times)

def book_appointment(patient_id: int, doctor_id: int, appointment_date: str, appointment_time: str, reason: str, initial_status: str = "Pending") -> tuple[int | None, str]:
    """Books a new appointment with double booking validation."""
    if isinstance(appointment_date, date):
        appointment_date = appointment_date.strftime("%Y-%m-%d")

    target_d = datetime.strptime(appointment_date, "%Y-%m-%d").date()
    if target_d < date.today():
        return None, "Appointment date cannot be in the past."

    conn = get_connection()
    cursor = conn.cursor()

    # Check Doctor availability
    cursor.execute("SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,))
    doc_row = cursor.fetchone()
    if not doc_row:
        conn.close()
        return None, "Selected doctor does not exist."

    doc_info = dict(doc_row)
    if doc_info["status"] != "Active":
        conn.close()
        return None, "Selected doctor is not active."

    if not is_doctor_available_on_date(doc_info["available_days"], target_d):
        conn.close()
        day_name = target_d.strftime("%A")
        return None, f"Doctor is not available on {day_name}s."

    # Check if doctor slot is already booked
    cursor.execute("""
        SELECT appointment_id FROM appointments
        WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ? AND status != 'Cancelled'
    """, (doctor_id, appointment_date, appointment_time))
    if cursor.fetchone():
        conn.close()
        return None, f"Slot {appointment_time} on {appointment_date} is already booked for Dr. {doc_info['full_name']}."

    # Check if patient already booked this doctor at same date/time
    cursor.execute("""
        SELECT appointment_id FROM appointments
        WHERE patient_id = ? AND doctor_id = ? AND appointment_date = ? AND appointment_time = ? AND status != 'Cancelled'
    """, (patient_id, doctor_id, appointment_date, appointment_time))
    if cursor.fetchone():
        conn.close()
        return None, "You already have an active appointment scheduled for this exact time slot."

    try:
        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (patient_id, doctor_id, appointment_date, appointment_time, reason, initial_status))
        appointment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return appointment_id, ""
    except Exception as e:
        conn.close()
        return None, f"Database error booking appointment: {str(e)}"

def get_all_appointments(patient_id_filter: int | None = None, doctor_id_filter: int | None = None, date_filter: str = None, status_filter: str = "All", search_term: str = "") -> list[dict]:
    """Retrieves appointments with optional patient, doctor, date, and status filters."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.*, p.full_name as patient_name, p.phone as patient_phone,
               d.full_name as doctor_name, d.specialization, d.room_number, d.consultation_fee
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE 1=1
    """
    params = []

    if patient_id_filter:
        query += " AND a.patient_id = ?"
        params.append(patient_id_filter)

    if doctor_id_filter:
        query += " AND a.doctor_id = ?"
        params.append(doctor_id_filter)

    if date_filter:
        query += " AND a.appointment_date = ?"
        params.append(str(date_filter))

    if status_filter and status_filter != "All":
        query += " AND a.status = ?"
        params.append(status_filter)

    if search_term:
        query += " AND (p.full_name LIKE ? OR d.full_name LIKE ? OR a.reason LIKE ?)"
        term = f"%{search_term.strip()}%"
        params.extend([term, term, term])

    query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def update_appointment_status(appointment_id: int, new_status: str) -> tuple[bool, str]:
    """Updates status of an appointment ('Pending', 'Confirmed', 'Completed', 'Cancelled')."""
    valid_statuses = ['Pending', 'Confirmed', 'Completed', 'Cancelled']
    if new_status not in valid_statuses:
        return False, f"Invalid status. Must be one of {valid_statuses}"

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE appointments SET status = ? WHERE appointment_id = ?", (new_status, appointment_id))
        conn.commit()
        conn.close()
        return True, f"Appointment status updated to '{new_status}'."
    except Exception as e:
        conn.close()
        return False, f"Database error: {str(e)}"

def delete_appointment(appointment_id: int) -> tuple[bool, str]:
    """Deletes an appointment."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM appointments WHERE appointment_id = ?", (appointment_id,))
        conn.commit()
        conn.close()
        return True, "Appointment deleted successfully."
    except Exception as e:
        conn.close()
        return False, f"Database error deleting appointment: {str(e)}"
