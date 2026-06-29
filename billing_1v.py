import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime

BILLING_FILE = "data/billing.csv"
ICD_FILE = "data/icd_master.csv"


# -----------------------------
# Initialize files
# -----------------------------
def initialize():
    os.makedirs("data", exist_ok=True)

    # Updated billing schema
    if not os.path.exists(BILLING_FILE):
        billing_df = pd.DataFrame(columns=[
            "bill_id",
            "patient_id",
            "icd_code",
            "medicine_cost",
            "consultation_fee",
            "total",
            "date"
        ])
        billing_df.to_csv(BILLING_FILE, index=False)

    # Updated ICD schema
    if not os.path.exists(ICD_FILE):
        icd_df = pd.DataFrame([
            {"icd_code": "A00", "description": "Cholera", "category": "Infectious"},
            {"icd_code": "E11", "description": "Type 2 Diabetes", "category": "Endocrine"},
            {"icd_code": "I10", "description": "Hypertension", "category": "Cardio"}
        ])
        icd_df.to_csv(ICD_FILE, index=False)


# -----------------------------
# Load ICD Master
# -----------------------------
def load_icd():
    icd_df = pd.read_csv(ICD_FILE)

    codes = np.array(icd_df["icd_code"])
    descriptions = np.array(icd_df["description"])
    categories = np.array(icd_df["category"])

    return icd_df, codes, descriptions, categories


# -----------------------------
# Fast ICD lookup
# -----------------------------
def find_icd(icd_code, codes, descriptions, categories):
    matches = np.where(codes == icd_code)[0]

    if len(matches) > 0:
        idx = matches[0]
        return descriptions[idx], categories[idx]

    return None, None


# -----------------------------
# Bill ID Generator
# -----------------------------
def generate_bill_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"BILL{timestamp}"


# -----------------------------
# Main Billing Page
# -----------------------------
def billing_page():
    initialize()

    st.title("🏥 Hospital ICD Billing System")

    icd_df, codes, descriptions, categories = load_icd()

    tab1, tab2, tab3 = st.tabs([
        "Generate Bill",
        "Search ICD",
        "Billing History"
    ])

    # =============================
    # TAB 1: Generate Bill
    # =============================
    with tab1:
        st.subheader("Generate Patient Bill")

        patient_id = st.text_input("Patient ID")
        icd_code = st.text_input("ICD Code").upper()

        medicine_cost = st.number_input("Medicine Cost (₹)", min_value=0.0, value=0.0)
        consultation_fee = st.number_input("Consultation Fee (₹)", min_value=0.0, value=0.0)

        if st.button("Generate Bill"):
            description, category = find_icd(icd_code, codes, descriptions, categories)

            if description:
                total = medicine_cost + consultation_fee

                st.success("Bill Generated Successfully")

                st.write("### Bill Summary")
                st.write("Patient ID:", patient_id)
                st.write("ICD Code:", icd_code)
                st.write("Disease:", description)
                st.write("Category:", category)
                st.write("Medicine Cost: ₹", medicine_cost)
                st.write("Consultation Fee: ₹", consultation_fee)
                st.write("## Total Amount: ₹", round(total, 2))

                billing_df = pd.read_csv(BILLING_FILE)

                new_bill = pd.DataFrame([{
                    "bill_id": generate_bill_id(),
                    "patient_id": patient_id,
                    "icd_code": icd_code,
                    "medicine_cost": medicine_cost,
                    "consultation_fee": consultation_fee,
                    "total": round(total, 2),
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])

                billing_df = pd.concat([billing_df, new_bill], ignore_index=True)
                billing_df.to_csv(BILLING_FILE, index=False)

            else:
                st.error("ICD code not found")

    # =============================
    # TAB 2: Search ICD
    # =============================
    with tab2:
        st.subheader("Search ICD Codes")

        search = st.text_input("Search by disease or category")

        if search:
            filtered = icd_df[
                icd_df["description"].str.contains(search, case=False, na=False) |
                icd_df["category"].str.contains(search, case=False, na=False)
            ]

            if len(filtered) > 0:
                st.dataframe(filtered)
            else:
                st.warning("No matching ICD records found")

    # =============================
    # TAB 3: Billing History
    # =============================
    with tab3:
        st.subheader("Billing History")

        billing_df = pd.read_csv(BILLING_FILE)

        if len(billing_df) > 0:
            st.dataframe(billing_df)

            total_revenue = billing_df["total"].sum()
            total_bills = len(billing_df)

            st.metric("Total Bills", total_bills)
            st.metric("Total Revenue", f"₹ {round(total_revenue, 2)}")
        else:
            st.info("No billing records available")