import streamlit as st
import pandas as pd
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

# --------------------------
# ICD MASTER DATABASE
# --------------------------
ICD_MASTER = {
    "I10": {"diagnosis": "Hypertension", "charge": 5000},
    "E11.9": {"diagnosis": "Type 2 Diabetes Mellitus", "charge": 8000},
    "J18.9": {"diagnosis": "Pneumonia", "charge": 12000},
    "N39.0": {"diagnosis": "Urinary Tract Infection", "charge": 7000},
    "K21.9": {"diagnosis": "GERD", "charge": 6500},
    "A09": {"diagnosis": "Gastroenteritis", "charge": 4500},
}

# --------------------------
# SESSION STATE
# --------------------------
if "selected_icd" not in st.session_state:
    st.session_state.selected_icd = []

# --------------------------
# FUNCTIONS
# --------------------------
def add_icd(code):
    code = code.strip().upper()
    if code in ICD_MASTER:
        if code not in st.session_state.selected_icd:
            st.session_state.selected_icd.append(code)
            return True, f"Added ICD code {code}"
        else:
            return False, "ICD already added"
    return False, "Invalid ICD code"

def calculate_total():
    total = 0
    rows = []

    for code in st.session_state.selected_icd:
        diagnosis = ICD_MASTER[code]["diagnosis"]
        charge = ICD_MASTER[code]["charge"]
        total += charge
        rows.append([code, diagnosis, charge])

    return total, rows

def generate_summary(patient, rows, total):
    summary = f"""
DISCHARGE SUMMARY
------------------------------------
Patient Name: {patient['name']}
Age: {patient['age']}
Gender: {patient['gender']}
Admission Date: {patient['admission']}
Discharge Date: {patient['discharge']}

Final Diagnosis:
"""

    for row in rows:
        summary += f"\n- {row[0]} : {row[1]} (Rs {row[2]})"

    summary += f"""

Treatment Provided:
- Clinical observation
- Medication
- Monitoring

Discharge Status:
Stable

Total Charges: Rs {total}

Advice:
- Continue medicines
- Follow-up after 7 days
"""
    return summary

def create_pdf(summary_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    for line in summary_text.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 5))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --------------------------
# UI
# --------------------------
st.title("🏥 Hospital Discharge Summary with ICD Scanner")

st.subheader("Patient Details")

name = st.text_input("Patient Name")
age = st.number_input("Age", min_value=1, max_value=120)
gender = st.selectbox("Gender", ["Male", "Female", "Other"])
admission = st.date_input("Admission Date", date.today())
discharge = st.date_input("Discharge Date", date.today())

st.subheader("Scan / Enter ICD Code")

scanned_code = st.text_input(
    "ICD Code (Scanner or Manual Entry)",
    placeholder="Example: E11.9"
)

if st.button("Add ICD"):
    success, msg = add_icd(scanned_code)
    if success:
        st.success(msg)
    else:
        st.error(msg)

if st.session_state.selected_icd:
    total, rows = calculate_total()

    st.subheader("Selected Diagnoses")

    df = pd.DataFrame(rows, columns=["ICD Code", "Diagnosis", "Charge"])
    st.table(df)

    st.metric("Total Charges", f"Rs {total}")

    if st.button("Generate Discharge Summary"):
        patient = {
            "name": name,
            "age": age,
            "gender": gender,
            "admission": admission,
            "discharge": discharge
        }

        summary = generate_summary(patient, rows, total)

        st.subheader("Generated Summary")
        st.text(summary)

        pdf = create_pdf(summary)

        st.download_button(
            label="Download PDF",
            data=pdf,
            file_name="discharge_summary.pdf",
            mime="application/pdf"
        )

if st.button("Reset"):
    st.session_state.selected_icd = []
    st.rerun()