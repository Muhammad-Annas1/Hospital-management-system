from database.db import get_connection

def create_tables():
    """Create database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Patients Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        date_of_birth TEXT NOT NULL,
        age INTEGER NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        blood_group TEXT,
        disease_problem TEXT,
        emergency_contact TEXT,
        registration_date TEXT NOT NULL,
        registration_time TEXT NOT NULL DEFAULT '09:00 AM',
        status TEXT NOT NULL DEFAULT 'Active'
    );

    """)

    # Doctors Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        qualification TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        experience_years INTEGER NOT NULL,
        consultation_fee REAL NOT NULL,
        available_days TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        slot_duration INTEGER NOT NULL DEFAULT 30,
        room_number TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active'
    );
    """)

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        patient_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
    );
    """)

    # Disease Specialization Mapping Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disease_mappings (
        mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
        disease_keyword TEXT UNIQUE NOT NULL,
        recommended_specialization TEXT NOT NULL
    );
    """)

    # Appointments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        reason TEXT,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
    );
    """)

    # Bills Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        appointment_id INTEGER UNIQUE NOT NULL,
        consultation_fee REAL NOT NULL DEFAULT 0.0,
        medicine_charges REAL NOT NULL DEFAULT 0.0,
        laboratory_charges REAL NOT NULL DEFAULT 0.0,
        other_charges REAL NOT NULL DEFAULT 0.0,
        discount REAL NOT NULL DEFAULT 0.0,
        tax REAL NOT NULL DEFAULT 0.0,
        total_amount REAL NOT NULL DEFAULT 0.0,
        payment_status TEXT NOT NULL DEFAULT 'Pending',
        payment_method TEXT NOT NULL DEFAULT 'Cash',
        bill_date TEXT NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
        FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
