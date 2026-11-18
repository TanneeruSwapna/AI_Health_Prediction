
import streamlit as st
import pandas as pd
from datetime import date

from db import (
    create_table,
    add_patient,
    get_all_patients,
    get_patient_by_id,
    update_patient,
    delete_patient
)

from validation import validate_patient
from ai_service import generate_health_remarks


# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="AI Health Prediction System",
    page_icon="🏥",
    layout="wide"
)

create_table()

st.title("🏥 AI Health Prediction System")
st.caption(
    "Patient Management | Health Records | AI-generated Observations"
)


# =====================================
# HELPER FUNCTION
# =====================================

def get_ai_remarks(glucose, haemoglobin, cholesterol):

    try:
        with st.spinner("Generating AI health remarks..."):

            remarks = generate_health_remarks(
                glucose,
                haemoglobin,
                cholesterol
            )

        return remarks

    except Exception as error:

        print("AI Error:", error)

        return (
            "AI remarks are temporarily unavailable. "
            "Please consult a qualified healthcare professional."
        )


# =====================================
# SIDEBAR NAVIGATION
# =====================================

menu = st.sidebar.radio(
    "Navigation",
    [
        "Add Patient",
        "View Patients",
        "Update Patient",
        "Delete Patient"
    ]
)


# =====================================
# 1. ADD PATIENT
# =====================================

if menu == "Add Patient":

    st.header("➕ Add New Patient")

    with st.form("add_patient_form", enter_to_submit=False):

        full_name = st.text_input("Patient Name")

        dob = st.date_input(
            "Date of Birth",
            value=date(1990, 1, 1),
            min_value=date(1950, 1, 1),
            max_value=date(2030, 12, 31)
        )

        email = st.text_input("Email Address")

        st.subheader("Health Details")

        col1, col2, col3 = st.columns(3)

        with col1:
            glucose = st.number_input(
                "Glucose",
                min_value=0.0,
                value=100.0,
                step=1.0
            )

        with col2:
            haemoglobin = st.number_input(
                "Haemoglobin",
                min_value=0.0,
                value=13.0,
                step=0.1
            )

        with col3:
            cholesterol = st.number_input(
                "Cholesterol",
                min_value=0.0,
                value=180.0,
                step=1.0
            )

        submitted = st.form_submit_button(
            "Save Patient",
            type="primary",
            width="stretch"
        )

    # Save patient after validation

    if submitted:

        errors = validate_patient(
            full_name,
            dob.isoformat(),
            email,
            glucose,
            haemoglobin,
            cholesterol
        )

        if errors:

            st.error("Please correct the following errors:")

            for error in errors:
                st.warning(error)

        else:

            try:

                patient_id = add_patient(
                    full_name.strip(),
                    dob.isoformat(),
                    email.strip(),
                    glucose,
                    haemoglobin,
                    cholesterol,
                    "AI remarks not generated yet."
                )

                st.session_state["latest_patient_id"] = patient_id

                st.session_state.pop("generated_remarks", None)

                st.success(
                    f"Patient saved successfully! Patient ID: {patient_id}"
                )

            except Exception as error:

                st.error(f"Database error: {error}")

    # Generate AI remarks separately after saving

    if "latest_patient_id" in st.session_state:

        latest_id = st.session_state["latest_patient_id"]

        patient = get_patient_by_id(latest_id)

        if patient:

            st.divider()

            st.subheader("AI Health Remarks")

            st.write(f"Patient: **{patient['full_name']}**")

            if st.button("Generate AI Remarks", type="primary"):

                remarks = get_ai_remarks(
                    patient["glucose"],
                    patient["haemoglobin"],
                    patient["cholesterol"]
                )

                if (
                    remarks.startswith("AI remarks are temporarily unavailable")
                    or remarks.startswith("AI remarks unavailable:")
                    or remarks == "AI remarks could not be generated."
                ):
                    st.warning(remarks)

                else:
                    updated = update_patient(
                        patient["id"],
                        patient["full_name"],
                        patient["dob"],
                        patient["email"],
                        patient["glucose"],
                        patient["haemoglobin"],
                        patient["cholesterol"],
                        remarks
                    )

                    if updated:
                        st.session_state["generated_remarks"] = remarks
                        st.success("AI remarks generated and saved successfully!")
                        st.rerun()
                    else:
                        st.error("Could not save AI remarks.")


# =====================================
# 2. VIEW PATIENTS
# =====================================

elif menu == "View Patients":

    st.header("📋 Patient Records")

    patients = get_all_patients()

    if patients:

        df = pd.DataFrame(patients)

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

        st.divider()

        st.subheader("View Individual Patient")

        selected_id = st.number_input(
            "Enter Patient ID",
            min_value=1,
            step=1,
            key="view_patient_id"
        )

        if st.button("Show Patient Details"):

            patient = get_patient_by_id(selected_id)

            if patient:

                st.write("**Patient Name:**", patient["full_name"])
                st.write("**Date of Birth:**", patient["dob"])
                st.write("**Email:**", patient["email"])
                st.write("**Glucose:**", patient["glucose"])
                st.write("**Haemoglobin:**", patient["haemoglobin"])
                st.write("**Cholesterol:**", patient["cholesterol"])

                st.subheader("AI Health Remarks")
                st.write(patient["remarks"])

            else:

                st.error("Patient ID not found.")

    else:

        st.info("No patient records found. Add a patient first.")


# =====================================
# 3. UPDATE PATIENT
# =====================================

elif menu == "Update Patient":

    st.header("✏️ Update Patient Details")

    # Display success message after update

    if st.session_state.get("update_success"):

        st.success(st.session_state["update_success"])

        del st.session_state["update_success"]

    patient_id = st.number_input(
        "Enter Patient ID",
        min_value=1,
        step=1,
        key="update_patient_id"
    )

    if st.button("Load Patient Details"):

        patient = get_patient_by_id(patient_id)

        if patient:

            st.session_state["edit_patient"] = patient

        else:

            st.session_state.pop("edit_patient", None)

            st.error("Patient not found.")

    if "edit_patient" in st.session_state:

        patient = st.session_state["edit_patient"]

        st.subheader(f"Editing: {patient['full_name']}")

        with st.form("update_patient_form"):

            full_name = st.text_input(
                "Patient Name",
                value=patient["full_name"]
            )

            dob = st.date_input(
                "Date of Birth",
                value=date.fromisoformat(patient["dob"]),
                max_value=date.today()
            )

            email = st.text_input(
                "Email Address",
                value=patient["email"]
            )

            glucose = st.number_input(
                "Glucose",
                min_value=0.0,
                value=float(patient["glucose"])
            )

            haemoglobin = st.number_input(
                "Haemoglobin",
                min_value=0.0,
                value=float(patient["haemoglobin"])
            )

            cholesterol = st.number_input(
                "Cholesterol",
                min_value=0.0,
                value=float(patient["cholesterol"])
            )

            update_button = st.form_submit_button(
                "Update Patient",
                type="primary"
            )

        if update_button:

            errors = validate_patient(
                full_name,
                dob.isoformat(),
                email,
                glucose,
                haemoglobin,
                cholesterol
            )

            if errors:

                for error in errors:
                    st.error(error)

            else:

                try:

                    updated = update_patient(
                        patient["id"],
                        full_name.strip(),
                        dob.isoformat(),
                        email.strip(),
                        glucose,
                        haemoglobin,
                        cholesterol,
                        "Patient details updated. AI remarks need to be regenerated."
                    )

                    if updated:

                        st.session_state["update_success"] = (
                            f"Patient {full_name} (ID: {patient['id']}) "
                            "updated successfully!"
                        )

                        st.session_state.pop("edit_patient", None)

                        st.rerun()

                    else:

                        st.error(
                            "No changes were saved. Patient ID not found."
                        )

                except Exception as error:

                    st.error(f"Database error: {error}")


# =====================================
# 4. DELETE PATIENT
# =====================================

elif menu == "Delete Patient":

    st.header("🗑️ Delete Patient Record")

    patient_id = st.number_input(
        "Enter Patient ID",
        min_value=1,
        step=1,
        key="delete_patient_id"
    )

    if st.button("Delete Patient", type="primary"):

        patient = get_patient_by_id(patient_id)

        if patient:

            deleted = delete_patient(patient_id)

            if deleted:

                st.success(
                    f"Patient {patient['full_name']} deleted successfully!"
                )

        else:

            st.error("Patient ID not found.")
