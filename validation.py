
import re
from datetime import date


def validate_patient(full_name, dob, email, glucose, haemoglobin, cholesterol):

    errors = []

    # Name validation
    if not full_name or not full_name.strip():
        errors.append("Patient name is required.")

    # Date of birth validation
    if not dob:
        errors.append("Date of birth is required.")
    else:
        try:
            dob_date = date.fromisoformat(str(dob))
            if dob_date >= date.today():
                errors.append("Date of birth must be in the past.")
        except ValueError:
            errors.append("Invalid date of birth.")

    # Email validation
    if not email or not re.match(r"^[\w.-]+@[\w.-]+\.[A-Za-z]{2,}$", email):
        errors.append("Please enter a valid email address.")

    # Health value validation
    try:
        if not 40 <= float(glucose) <= 500:
            errors.append("Glucose must be between 40 and 500.")
    except (ValueError, TypeError):
        errors.append("Glucose must be a valid number.")

    try:
        if not 3 <= float(haemoglobin) <= 25:
            errors.append("Haemoglobin must be between 3 and 25.")
    except (ValueError, TypeError):
        errors.append("Haemoglobin must be a valid number.")

    try:
        if not 50 <= float(cholesterol) <= 500:
            errors.append("Cholesterol must be between 50 and 500.")
    except (ValueError, TypeError):
        errors.append("Cholesterol must be a valid number.")

    return errors
