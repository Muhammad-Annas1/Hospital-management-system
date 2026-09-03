from database.db import get_connection
from utils.validators import validate_non_negative
from datetime import date

def calculate_totals(consultation_fee: float, medicine_charges: float, laboratory_charges: float, other_charges: float, discount: float, tax: float) -> dict:
    """Calculates subtotal and total amount ensured to be non-negative."""
    c_fee = max(0.0, float(consultation_fee or 0.0))
    m_fee = max(0.0, float(medicine_charges or 0.0))
    l_fee = max(0.0, float(laboratory_charges or 0.0))
    o_fee = max(0.0, float(other_charges or 0.0))
    disc = max(0.0, float(discount or 0.0))
    tx = max(0.0, float(tax or 0.0))

    subtotal = c_fee + m_fee + l_fee + o_fee
    total = max(0.0, subtotal - disc + tx)

    return {
        "consultation_fee": c_fee,
        "medicine_charges": m_fee,
        "laboratory_charges": l_fee,
        "other_charges": o_fee,
        "subtotal": subtotal,
        "discount": disc,
        "tax": tx,
        "total_amount": round(total, 2)
    }

def create_bill(data: dict) -> tuple[int | None, str]:
    """Creates a new bill for an appointment."""
    patient_id = data.get("patient_id")
    appointment_id = data.get("appointment_id")
    c_fee = data.get("consultation_fee", 0.0)
    m_fee = data.get("medicine_charges", 0.0)
    l_fee = data.get("laboratory_charges", 0.0)
    o_fee = data.get("other_charges", 0.0)
    discount = data.get("discount", 0.0)
    tax = data.get("tax", 0.0)
    payment_status = data.get("payment_status", "Pending")
    payment_method = data.get("payment_method", "Cash")
    bill_date = data.get("bill_date", date.today().strftime("%Y-%m-%d"))

    if not patient_id or not appointment_id:
        return None, "Patient and Appointment are required to generate a bill."

    calc = calculate_totals(c_fee, m_fee, l_fee, o_fee, discount, tax)

    conn = get_connection()
    cursor = conn.cursor()

    # Check if bill already exists for this appointment
    cursor.execute("SELECT bill_id FROM bills WHERE appointment_id = ?", (appointment_id,))
    if cursor.fetchone():
        conn.close()
        return None, "A bill has already been created for this appointment."

    try:
        cursor.execute("""
            INSERT INTO bills (patient_id, appointment_id, consultation_fee, medicine_charges, laboratory_charges, other_charges, discount, tax, total_amount, payment_status, payment_method, bill_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, appointment_id, calc["consultation_fee"], calc["medicine_charges"], calc["laboratory_charges"], calc["other_charges"], calc["discount"], calc["tax"], calc["total_amount"], payment_status, payment_method, str(bill_date)))
        bill_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return bill_id, ""
    except Exception as e:
        conn.close()
        return None, f"Database error creating bill: {str(e)}"

def update_bill(bill_id: int, data: dict) -> tuple[bool, str]:
    """Updates an existing bill."""
    c_fee = data.get("consultation_fee", 0.0)
    m_fee = data.get("medicine_charges", 0.0)
    l_fee = data.get("laboratory_charges", 0.0)
    o_fee = data.get("other_charges", 0.0)
    discount = data.get("discount", 0.0)
    tax = data.get("tax", 0.0)
    payment_status = data.get("payment_status", "Pending")
    payment_method = data.get("payment_method", "Cash")
    bill_date = data.get("bill_date")

    calc = calculate_totals(c_fee, m_fee, l_fee, o_fee, discount, tax)

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE bills
            SET consultation_fee = ?, medicine_charges = ?, laboratory_charges = ?, other_charges = ?,
                discount = ?, tax = ?, total_amount = ?, payment_status = ?, payment_method = ?, bill_date = ?
            WHERE bill_id = ?
        """, (calc["consultation_fee"], calc["medicine_charges"], calc["laboratory_charges"], calc["other_charges"], calc["discount"], calc["tax"], calc["total_amount"], payment_status, payment_method, str(bill_date), bill_id))
        conn.commit()
        conn.close()
        return True, "Bill updated successfully!"
    except Exception as e:
        conn.close()
        return False, f"Database error updating bill: {str(e)}"

def delete_bill(bill_id: int) -> tuple[bool, str]:
    """Deletes a bill."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM bills WHERE bill_id = ?", (bill_id,))
        conn.commit()
        conn.close()
        return True, "Bill deleted successfully!"
    except Exception as e:
        conn.close()
        return False, f"Database error deleting bill: {str(e)}"

def get_all_bills(patient_id_filter: int | None = None, payment_status_filter: str = "All", search_term: str = "", date_filter: str = None) -> list[dict]:
    """Retrieves bills with joined patient and appointment metadata."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT b.*, p.full_name as patient_name, p.phone as patient_phone,
               a.appointment_date, a.appointment_time, d.full_name as doctor_name, d.specialization
        FROM bills b
        JOIN patients p ON b.patient_id = p.patient_id
        JOIN appointments a ON b.appointment_id = a.appointment_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE 1=1
    """
    params = []

    if patient_id_filter:
        query += " AND b.patient_id = ?"
        params.append(patient_id_filter)

    if payment_status_filter and payment_status_filter != "All":
        query += " AND b.payment_status = ?"
        params.append(payment_status_filter)

    if date_filter:
        query += " AND b.bill_date = ?"
        params.append(str(date_filter))

    if search_term:
        query += " AND (p.full_name LIKE ? OR d.full_name LIKE ? OR b.bill_id LIKE ?)"
        term = f"%{search_term.strip()}%"
        params.extend([term, term, term])

    query += " ORDER BY b.bill_id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
