
import sqlite3
from pathlib import Path

# Database file location
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "health_prediction.db"


# Establish database connection
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Create patients table
def create_table():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            dob TEXT NOT NULL,
            email TEXT NOT NULL,
            glucose REAL NOT NULL,
            haemoglobin REAL NOT NULL,
            cholesterol REAL NOT NULL,
            remarks TEXT
        )
    """)

    conn.commit()
    conn.close()


# Create: Insert patient record
def add_patient(full_name, dob, email, glucose,
                haemoglobin, cholesterol, remarks):

    conn = get_connection()

    cursor = conn.execute("""
        INSERT INTO patients
        (full_name, dob, email, glucose, haemoglobin,
         cholesterol, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        full_name, dob, email, glucose,
        haemoglobin, cholesterol, remarks
    ))

    patient_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return patient_id


# Read: Retrieve all patient records
def get_all_patients():
    conn = get_connection()

    patients = conn.execute("""
        SELECT * FROM patients ORDER BY id
    """).fetchall()

    conn.close()

    return [dict(patient) for patient in patients]


# Read: Retrieve one patient using ID
def get_patient_by_id(patient_id):
    conn = get_connection()

    patient = conn.execute("""
        SELECT * FROM patients WHERE id = ?
    """, (patient_id,)).fetchone()

    conn.close()

    return dict(patient) if patient else None


# Update: Modify an existing patient
def update_patient(patient_id, full_name, dob, email,
                   glucose, haemoglobin, cholesterol, remarks):

    conn = get_connection()

    cursor = conn.execute("""
        UPDATE patients
        SET full_name = ?,
            dob = ?,
            email = ?,
            glucose = ?,
            haemoglobin = ?,
            cholesterol = ?,
            remarks = ?
        WHERE id = ?
    """, (
        full_name, dob, email, glucose,
        haemoglobin, cholesterol, remarks, patient_id
    ))

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()

    return updated


# Delete: Remove a patient record
def delete_patient(patient_id):
    conn = get_connection()

    cursor = conn.execute("""
        DELETE FROM patients WHERE id = ?
    """, (patient_id,))

    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()

    return deleted
