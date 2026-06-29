import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import qrcode

BILLING_FILE = "data/billing.csv"
ICD_FILE = "data/icd_master.csv"


# -----------------------------
# Initialize
# -----------------------------
def initialize():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(BILLING_FILE):
        pd.DataFrame(columns=[
            "bill_id",
            "patient_id",
            "icd_code",
            "medicine_cost",
            "consultation_fee",
            "total",
            "date"
        ]).to_csv(BILLING_FILE, index=False)


# -----------------------------
# Load ICD
# -----------------------------
def load_icd():
    return pd.read_csv(ICD_FILE)


# -----------------------------
# Bill ID
# -----------------------------
def generate_bill_id():
    return "BILL" + datetime.now().strftime("%Y%m%d%H%M%S")


# -----------------------------
# Generate QR
# -----------------------------
def generate_qr(bill):
    qr_data = json.dumps(bill)

    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    qr_path = f"data/{bill['bill_id']}_qr.png"
    img.save(qr_path)

    return qr_path


# -----------------------------
# PDF Generator
# -----------------------------
def generate_pdf(bill, qr_path):
    file_path = f"data/{bill['bill_id']}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Hospital Billing Invoice")

    c.setFont("Helvetica", 12)

    y = 760
    for k, v in bill.items():
        c.drawString(50, y, f"{k}: {v}")
        y -= 25

    # Add QR code to PDF
    c.drawImage(qr_path, 350, 620, width=150, height=150)

    c.setFont("Helvetica", 10)
    c.drawString(350, 610, "Scan QR to verify bill")

    c.save()
    return file_path


# -----------------------------
# Billing Page
# -----------------------------
def billing_page():
    initialize()

    st.title("🏥 Advanced Hospital Billing System with QR")

    icd_df = load_icd()

    tab1, tab2, tab3 = st.tabs([
        "Generate Bill",
        "ICD Search",
        "Billing History"
    ])

    # =========================
    # TAB 1
    # =========================
    with tab1:
        st.subheader("Generate Bill")

        patient_id = st.text_input("Patient ID")

        icd_selection = st.selectbox(
            "Select ICD Code",
            icd_df["icd_code"] + " - " + icd_df["description"]
        )

        icd_code = icd_selection.split(" - ")[0]

        row = icd_df[icd_df["icd_code"] == icd_code]

        medicine_cost = float(row["medicine_cost"].iloc[0])
        consultation_fee = float(row["consultation_fee"].iloc[0])

        st.write(f"Medicine Cost: ₹ {medicine_cost}")
        st.write(f"Consultation Fee: ₹ {consultation_fee}")

        if st.button("Generate Bill"):
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

            # Save billing record
            df = pd.read_csv(BILLING_FILE)
            df = pd.concat([df, pd.DataFrame([bill])], ignore_index=True)
            df.to_csv(BILLING_FILE, index=False)

            # Generate QR
            qr_path = generate_qr(bill)

            st.subheader("Bill QR Code")
            st.image(qr_path, width=250)

            # Generate PDF
            pdf_path = generate_pdf(bill, qr_path)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇ Download Bill PDF",
                    f,
                    file_name=f"{bill['bill_id']}.pdf"
                )

    # =========================
    # TAB 2
    # =========================
    with tab2:
        st.subheader("Search ICD")

        search = st.text_input("Search ICD")

        if search:
            result = icd_df[
                icd_df["description"].str.contains(search, case=False) |
                icd_df["category"].str.contains(search, case=False)
            ]
            st.dataframe(result)

    # =========================
    # TAB 3
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