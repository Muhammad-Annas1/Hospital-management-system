import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_connection
from database.schema import create_tables
from utils.helpers import hash_password
from utils.disease_rules import DEFAULT_DISEASE_MAPPINGS
from datetime import date, timedelta

def seed_database():
    """Populates the database with realistic sample demo data in PKR currency and full day schedules."""
    # Ensure tables exist first
    create_tables()

    conn = get_connection()
    cursor = conn.cursor()

    # Drop tables to apply schema changes on seed
    cursor.execute("PRAGMA foreign_keys = OFF;")
    cursor.execute("DROP TABLE IF EXISTS bills;")
    cursor.execute("DROP TABLE IF EXISTS appointments;")
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("DROP TABLE IF EXISTS doctors;")
    cursor.execute("DROP TABLE IF EXISTS patients;")
    cursor.execute("DROP TABLE IF EXISTS disease_mappings;")
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    # Recreate tables with updated schema
    create_tables()


    # 1. Admin Account
    admin_hash = hash_password("admin123")
    cursor.execute("""
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
    """, ("admin", admin_hash, "admin"))

    # 2. Seed Disease Mappings
    for disease, spec in DEFAULT_DISEASE_MAPPINGS.items():
        cursor.execute("""
            INSERT OR IGNORE INTO disease_mappings (disease_keyword, recommended_specialization)
            VALUES (?, ?)
        """, (disease, spec))

    # 3. Seed 8 Doctors with PKR fees and full available schedules
    doctors_data = [
        ("Dr. Sarah Jenkins", "Cardiologist", "MD, FACC - Harvard Medical", "+1-555-0101", "sarah.jenkins@hospital.org", 14, 2500.0, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday", "09:00", "21:00", 30, "Room 101", "Active"),
        ("Dr. Marcus Vance", "Dermatologist", "MD, Board Certified Dermatology", "+1-555-0102", "marcus.vance@hospital.org", 10, 2000.0, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday", "09:00", "21:00", 30, "Room 102", "Active"),
        ("Dr. Elena Rostova", "Neurologist", "MD, PhD Neuroscience", "+1-555-0103", "elena.rostova@hospital.org", 18, 3000.0, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday", "09:00", "21:00", 30, "Room 201", "Active"),
        ("Dr. Robert Chen", "Orthopedic", "MS Orthopedics - Johns Hopkins", "+1-555-0104", "robert.chen@hospital.org", 12, 2200.0, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday", "09:00", "21:00", 30, "Room 202", "Active"),
        ("Dr. Emily Watson", "Pediatrician", "MD Pediatrics - Stanford", "+1-555-0105", "emily.watson@hospital.org", 8, 1800.0, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday", "09:00", "21:00", 30, "Room 103", "Active"),
        ("Dr. Aisha Patel", "Gynecologist", "MD, OB/GYN Specialist", "+1-555-0106", "aisha.patel@hospital.org", 11, 2200.0, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday", "09:00", "21:00", 30, "Room 203", "Active"),
        ("Dr. James Thorne", "ENT Specialist", "MS Otorhinolaryngology", "+1-555-0107", "james.thorne@hospital.org", 15, 2000.0, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday", "09:00", "21:00", 30, "Room 104", "Active"),
        ("Dr. David Miller", "General Physician", "MBBS, MD Internal Medicine", "+1-555-0108", "david.miller@hospital.org", 20, 1500.0, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday", "09:00", "21:00", 30, "Room 105", "Active"),
    ]

    doctor_ids = []
    for doc in doctors_data:
        cursor.execute("""
            INSERT INTO doctors (full_name, specialization, qualification, phone, email, experience_years, consultation_fee, available_days, start_time, end_time, slot_duration, room_number, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, doc)
        doctor_ids.append(cursor.lastrowid)

    # 4. Seed 10 Patients & create credentials
    patients_data = [
        ("John Doe", "Male", "1985-04-12", 41, "+1-555-0201", "john.doe@example.com", "123 Maple St, Springfield", "O+", "Heart problem", "+1-555-0901", "2026-01-10", "09:15 AM", "Active", "john_doe", "pass123"),
        ("Alice Smith", "Female", "1992-08-25", 34, "+1-555-0202", "alice.smith@example.com", "456 Oak Ave, Springfield", "A+", "Skin problem / Rash / Acne", "+1-555-0902", "2026-01-15", "10:30 AM", "Active", "alice_smith", "pass123"),
        ("Michael Brown", "Male", "1978-11-30", 47, "+1-555-0203", "michael.brown@example.com", "789 Pine Rd, Metro City", "B+", "Brain / Nerves / Migraine", "+1-555-0903", "2026-02-01", "11:45 AM", "Active", "michael_brown", "pass123"),
        ("Emma Wilson", "Female", "1999-03-14", 27, "+1-555-0204", "emma.wilson@example.com", "321 Cedar Blvd, Metro City", "AB+", "Bone / Joint problem / Back pain", "+1-555-0904", "2026-02-05", "01:20 PM", "Active", "emma_wilson", "pass123"),
        ("Lucas Garcia", "Male", "2015-06-20", 11, "+1-555-0205", "lucas.garcia@example.com", "654 Elm St, Riverdale", "O-", "Child health / Pediatrics", "+1-555-0905", "2026-02-10", "02:15 PM", "Active", "lucas_garcia", "pass123"),
        ("Sophia Martinez", "Female", "1990-12-05", 35, "+1-555-0206", "sophia.m@example.com", "987 Walnut St, Riverdale", "A-", "Pregnancy / Women's health", "+1-555-0906", "2026-02-12", "03:30 PM", "Active", "sophia_m", "pass123"),
        ("David Clark", "Male", "1965-01-18", 61, "+1-555-0207", "david.clark@example.com", "159 Birch Ln, Lakeview", "B-", "Ear / Nose / Throat", "+1-555-0907", "2026-02-15", "04:10 PM", "Active", "david_clark", "pass123"),
        ("Olivia Taylor", "Female", "2001-09-09", 24, "+1-555-0208", "olivia.taylor@example.com", "753 Spruce St, Lakeview", "O+", "Fever / Common cold / General illness", "+1-555-0908", "2026-02-18", "05:00 PM", "Active", "olivia_taylor", "pass123"),
        ("Ethan Harris", "Male", "1988-07-22", 38, "+1-555-0209", "ethan.harris@example.com", "852 Ash Dr, Springfield", "AB-", "Dental / Tooth problem", "+1-555-0909", "2026-02-20", "06:25 PM", "Active", "ethan_harris", "pass123"),
        ("Mia Robinson", "Female", "1995-05-30", 31, "+1-555-0210", "mia.robinson@example.com", "951 Willow Way, Metro City", "A+", "Mental health / Anxiety / Stress", "+1-555-0910", "2026-02-22", "07:10 PM", "Active", "mia_robinson", "pass123"),
    ]

    patient_ids = []
    for pat in patients_data:
        full_name, gender, dob, age, phone, email, address, bg, dis, em, reg_date, reg_time, status, uname, pwd = pat
        cursor.execute("""
            INSERT INTO patients (full_name, gender, date_of_birth, age, phone, email, address, blood_group, disease_problem, emergency_contact, registration_date, registration_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (full_name, gender, dob, age, phone, email, address, bg, dis, em, reg_date, reg_time, status))
        p_id = cursor.lastrowid
        patient_ids.append(p_id)


        # Create user account for patient
        pwd_hash = hash_password(pwd)
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, patient_id)
            VALUES (?, ?, 'patient', ?)
        """, (uname, pwd_hash, p_id))

    # 5. Seed Appointments
    today = date.today()
    yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    next_week = (today + timedelta(days=3)).strftime("%Y-%m-%d")
    last_week = (today - timedelta(days=5)).strftime("%Y-%m-%d")

    appointments_sample = [
        (patient_ids[0], doctor_ids[0], yesterday, "09:30 AM", "Regular heart checkup", "Completed"),
        (patient_ids[1], doctor_ids[1], yesterday, "10:30 AM", "Skin allergy consultation", "Completed"),
        (patient_ids[2], doctor_ids[2], last_week, "11:00 AM", "Frequent migraine headaches", "Completed"),
        (patient_ids[3], doctor_ids[3], today.strftime("%Y-%m-%d"), "10:00 AM", "Knee joint pain", "Confirmed"),
        (patient_ids[4], doctor_ids[4], today.strftime("%Y-%m-%d"), "11:00 AM", "Child seasonal fever check", "Confirmed"),
        (patient_ids[5], doctor_ids[5], yesterday, "11:30 AM", "Routine prenatal checkup", "Completed"),
        (patient_ids[6], doctor_ids[6], last_week, "10:00 AM", "Chronic sinus inflammation", "Completed"),
        (patient_ids[7], doctor_ids[7], yesterday, "02:00 PM", "General physical exam", "Completed"),
        (patient_ids[8], doctor_ids[0], today.strftime("%Y-%m-%d"), "03:00 PM", "Dental tooth pain checkup", "Confirmed"),
        (patient_ids[9], doctor_ids[2], yesterday, "04:30 PM", "Stress and anxiety consultation", "Completed"),

    ]

    appointment_ids = []
    for app in appointments_sample:
        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, app)
        appointment_ids.append(cursor.lastrowid)

    # 6. Seed Bills in PKR for all 10 Patients
    bills_sample = [
        (patient_ids[0], appointment_ids[0], 2500.0, 500.0, 1000.0, 0.0, 200.0, 150.0, 2950.0, "Paid", "Card", yesterday),
        (patient_ids[1], appointment_ids[1], 2000.0, 300.0, 0.0, 0.0, 100.0, 100.0, 2300.0, "Paid", "Cash", yesterday),
        (patient_ids[2], appointment_ids[2], 3000.0, 1200.0, 1500.0, 300.0, 500.0, 250.0, 5750.0, "Partially Paid", "Bank Transfer", last_week),
        (patient_ids[3], appointment_ids[3], 2200.0, 800.0, 1000.0, 0.0, 0.0, 200.0, 4200.0, "Pending", "Cash", today.strftime("%Y-%m-%d")),
        (patient_ids[4], appointment_ids[4], 1800.0, 400.0, 0.0, 0.0, 100.0, 0.0, 2100.0, "Paid", "Card", today.strftime("%Y-%m-%d")),
        (patient_ids[5], appointment_ids[5], 2200.0, 600.0, 800.0, 0.0, 100.0, 100.0, 3600.0, "Paid", "Cash", yesterday),
        (patient_ids[6], appointment_ids[6], 2000.0, 500.0, 0.0, 0.0, 0.0, 100.0, 2600.0, "Pending", "Bank Transfer", last_week),
        (patient_ids[7], appointment_ids[7], 1500.0, 300.0, 500.0, 0.0, 100.0, 0.0, 2200.0, "Paid", "Cash", yesterday),
        (patient_ids[8], appointment_ids[8], 2000.0, 400.0, 600.0, 0.0, 0.0, 100.0, 3100.0, "Partially Paid", "Card", today.strftime("%Y-%m-%d")),
        (patient_ids[9], appointment_ids[9], 3000.0, 700.0, 0.0, 0.0, 200.0, 100.0, 3600.0, "Paid", "Cash", yesterday),
    ]

    for bill in bills_sample:
        cursor.execute("""
            INSERT INTO bills (patient_id, appointment_id, consultation_fee, medicine_charges, laboratory_charges, other_charges, discount, tax, total_amount, payment_status, payment_method, bill_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, bill)


    conn.commit()
    conn.close()

    from services.patient_service import sync_patients_json
    sync_patients_json()

    print("Database successfully seeded with PKR amounts & registered_patients.json synced!")


if __name__ == "__main__":
    seed_database()
