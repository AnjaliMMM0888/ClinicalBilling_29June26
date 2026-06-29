import streamlit as st
import pandas as pd
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# -----------------------------
# ICD MASTER DATA
# -----------------------------
icd_master = {
    "I10": {"diagnosis": "Hypertension", "charge": 5000},
    "E11.9": {"diagnosis": "Type 2 Diabetes", "charge": 8000},
    "J18.9": {"diagnosis": "Pneumonia", "charge": 12000},
    "N39.0": {"diagnosis": "Urinary Tract Infection", "charge": 7000},
    "K21.9": {"diagnosis": "GERD", "charge": 6500}
}

# -----------------------------
# FUNCTIONS
# -----------------------------
def calculate_total(selected_codes):
    total = 0
    diagnosis_list = []

    for code in selected_codes:
        diagnosis = icd_master[code]["diagnosis"]
        charge = icd_master[code]["charge"]
        total += charge
        diagnosis_list.append(f"{code} - {diagnosis} (Rs {charge})")

    return total, diagnosis_list


def generate_summary(patient_data, diagnosis_list, total):
    summary = f"""
DISCHARGE SUMMARY
-------------------------------------
Patient Name: {patient_data['name']}
Age: {patient_data['age']}
Gender: {patient_data['gender']}
Admission Date: {patient_data['admission']}
Discharge Date: {patient_data['discharge']}

Final Diagnosis:
"""

    for d in diagnosis_list:
        summary += f"\n- {d}"

    summary += f"""

Treatment Given:
• Clinical assessment
• Medication administered
• Monitoring & nursing care

Discharge Status:
Stable

Final Charges: Rs {total}

Advice:
• Continue prescribed medication
• Follow-up after 7 days
"""
    return summary


def create_pdf(summary_text):
    filename = "discharge_summary.pdf"
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    story = []

    for line in summary_text.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 5))

    doc.build(story)
    return filename


# -----------------------------
# UI
# -----------------------------
st.title("Hospital Discharge Summary Generator")

st.header("Patient Information")

name = st.text_input("Patient Name")
age = st.number_input("Age", 1, 120)
gender = st.selectbox("Gender", ["Male", "Female", "Other"])
admission = st.date_input("Admission Date", date.today())
discharge = st.date_input("Discharge Date", date.today())

st.header("Select ICD-10 Diagnosis")

selected_codes = st.multiselect(
    "Choose ICD Codes",
    list(icd_master.keys())
)

if selected_codes:
    rows = []
    for code in selected_codes:
        rows.append({
            "ICD Code": code,
            "Diagnosis": icd_master[code]["diagnosis"],
            "Charge": icd_master[code]["charge"]
        })

    df = pd.DataFrame(rows)
    st.table(df)

if st.button("Generate Discharge Summary"):
    patient_data = {
        "name": name,
        "age": age,
        "gender": gender,
        "admission": admission,
        "discharge": discharge
    }

    total, diagnosis_list = calculate_total(selected_codes)
    summary = generate_summary(patient_data, diagnosis_list, total)

    st.subheader("Generated Summary")
    st.text(summary)

    pdf_file = create_pdf(summary)

    with open(pdf_file, "rb") as f:
        st.download_button(
            "Download PDF",
            f,
            file_name="discharge_summary.pdf",
            mime="application/pdf"
        )