import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BILLING_FILE = "data/billing.csv"
ICD_FILE = "data/icd_master.csv"


# -----------------------------
# Initialize
# -----------------------------
def initialize():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(BILLING_FILE):
        pd.DataFrame(columns=[
            "bill_id", "patient_id", "icd_code",
            "medicine_cost", "consultation_fee",
            "total", "date"
        ]).to_csv(BILLING_FILE, index=False)

    if not os.path.exists(ICD_FILE):
        pd.DataFrame([
            {"icd_code": "A00", "description": "Cholera", "category": "Infectious"},
            {"icd_code": "E11", "description": "Type 2 Diabetes", "category": "Endocrine"},
            {"icd_code": "I10", "description": "Hypertension", "category": "Cardio"}
        ]).to_csv(ICD_FILE, index=False)


# -----------------------------
# Load ICD
# -----------------------------
def load_icd():
    df = pd.read_csv(ICD_FILE)
    return df


# -----------------------------
# Bill ID
# -----------------------------
def generate_bill_id():
    return "BILL" + datetime.now().strftime("%Y%m%d%H%M%S")


# -----------------------------
# PDF Generator
# -----------------------------
def generate_pdf(bill):
    file_path = f"data/{bill['bill_id']}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    c.setFont("Helvetica", 12)

    y = 800
    for k, v in bill.items():
        c.drawString(50, y, f"{k}: {v}")
        y -= 30

    c.save()
    return file_path


# -----------------------------
# App
# -----------------------------
def billing_page():
    initialize()

    st.title("🏥 Advanced Hospital Billing System V2")

    icd_df = load_icd()

    tab1, tab2, tab3 = st.tabs(["Generate Bill", "ICD Search", "Billing History"])


    # =========================
    # TAB 1 - BILL GENERATION
    # =========================
    with tab1:
        st.subheader("Generate Bill")

        patient_id = st.text_input("Patient ID")

        # Smart ICD selection
        icd_code = st.selectbox(
            "Select ICD Code",
            icd_df["icd_code"] + " - " + icd_df["description"]
        )
        icd_code = icd_code.split(" - ")[0]

        medicine_cost = st.number_input("Medicine Cost", min_value=0.0)
        consultation_fee = st.number_input("Consultation Fee", min_value=0.0)

        if st.button("Generate Bill"):

            icd_row = icd_df[icd_df["icd_code"] == icd_code]

            if not icd_row.empty:

                total = medicine_cost + consultation_fee

                bill = {
                    "bill_id": generate_bill_id(),
                    "patient_id": patient_id,
                    "icd_code": icd_code,
                    "medicine_cost": medicine_cost,
                    "consultation_fee": consultation_fee,
                    "total": total,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                st.success("Bill Generated Successfully")
                st.json(bill)

                # Save
                df = pd.read_csv(BILLING_FILE)
                df = pd.concat([df, pd.DataFrame([bill])], ignore_index=True)
                df.to_csv(BILLING_FILE, index=False)

                # PDF
                pdf_path = generate_pdf(bill)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "⬇ Download Bill PDF",
                        f,
                        file_name=f"{bill['bill_id']}.pdf"
                    )


    # =========================
    # TAB 2 - ICD SEARCH
    # =========================
    with tab2:
        st.subheader("Search ICD Codes")

        search = st.text_input("Search ICD")

        if search:
            result = icd_df[
                icd_df["description"].str.contains(search, case=False) |
                icd_df["category"].str.contains(search, case=False)
            ]
            st.dataframe(result)


    # =========================
    # TAB 3 - HISTORY
    # =========================
    with tab3:
        st.subheader("Billing History")

        df = pd.read_csv(BILLING_FILE)

        if len(df) > 0:
            st.dataframe(df)
            st.metric("Total Bills", len(df))
            st.metric("Total Revenue", f"₹ {df['total'].sum()}")
        else:
            st.info("No records found")
