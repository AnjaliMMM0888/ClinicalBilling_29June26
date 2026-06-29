import streamlit as st
from reportlab.pdfgen import canvas

def discharge_summary():
    st.title("Discharge Summary")

    patient_id = st.text_input("Patient ID")
    notes = st.text_area("Doctor Notes")

    if st.button("Generate PDF"):
        filename = f"{patient_id}_summary.pdf"
        c = canvas.Canvas(filename)

        c.drawString(100, 800, "Hospital Discharge Summary")
        c.drawString(100, 760, f"Patient ID: {patient_id}")
        c.drawString(100, 720, f"Notes: {notes}")

        c.save()

        st.success("PDF generated")