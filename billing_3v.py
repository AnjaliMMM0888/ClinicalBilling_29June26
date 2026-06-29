import streamlit as st
import pandas as pd
import os
from datetime import datetime

BILLING_FILE = "data/billing.csv"
ICD_FILE = "data/icd_master.csv"


# -----------------------------
# Initialize files
# -----------------------------
def initialize():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(BILLING_FILE):
        pd.DataFrame(columns=[
            "bill_id",
            "patient_id",
            "icd_code",
            "description",
            "category",
            "medicine_cost",
            "consultation_fee",
            "total",
            "date"
        ]).to_csv(BILLING_FILE, index=False)


# -----------------------------
# Bill ID
# -----------------------------
def generate_bill_id():
    return "BILL" + datetime.now().strftime("%Y%m%d%H%M%S")


# -----------------------------
# Load ICD Master
# -----------------------------
def load_icd():
    return pd.read_csv(ICD_FILE)


# -----------------------------
# MAIN APP
# -----------------------------
def billing_page():
    initialize()

    st.title("🏥 Smart Hospital Billing System")

    icd_df = load_icd()

    tab1, tab2, tab3 = st.tabs(["Generate Bill", "ICD Search", "Billing History"])


    # =========================
    # TAB 1 - BILL GENERATION
    # =========================
    with tab1:
        st.subheader("Generate Patient Bill")

        patient_id = st.text_input("Patient ID")

        # ICD dropdown
        icd_options = icd_df["icd_code"] + " - " + icd_df["description"]

        selected = st.selectbox("Select ICD Code", icd_options)

        icd_code = selected.split(" - ")[0]

        # AUTO FETCH DATA
        icd_row = icd_df[icd_df["icd_code"] == icd_code]

        if not icd_row.empty:
            description = icd_row["description"].values[0]
            category = icd_row["category"].values[0]
            medicine_cost = float(icd_row["medicine_cost"].values[0])
            consultation_fee = float(icd_row["consultation_fee"].values[0])

            total = medicine_cost + consultation_fee

            st.success("Auto-populated billing details")

            st.write("### ICD Details")
            st.write("Description:", description)
            st.write("Category:", category)

            st.write("### Cost Breakdown")
            st.write("Medicine Cost: ₹", medicine_cost)
            st.write("Consultation Fee: ₹", consultation_fee)
            st.write("## Total: ₹", total)

            if st.button("Generate Bill"):

                bill = {
                    "bill_id": generate_bill_id(),
                    "patient_id": patient_id,
                    "icd_code": icd_code,
                    "description": description,
                    "category": category,
                    "medicine_cost": medicine_cost,
                    "consultation_fee": consultation_fee,
                    "total": total,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                df = pd.read_csv(BILLING_FILE)
                df = pd.concat([df, pd.DataFrame([bill])], ignore_index=True)
                df.to_csv(BILLING_FILE, index=False)

                st.success("Bill Generated Successfully")
                st.json(bill)

        else:
            st.error("Invalid ICD selection")


    # =========================
    # TAB 2 - ICD SEARCH
    # =========================
    with tab2:
        st.subheader("Search ICD Codes")

        search = st.text_input("Search ICD / Category")

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

        if os.path.exists(BILLING_FILE):
            df = pd.read_csv(BILLING_FILE)

            if len(df) > 0:
                st.dataframe(df)

                st.metric("Total Bills", len(df))
                st.metric("Total Revenue", f"₹ {df['total'].sum():,.2f}")
            else:
                st.info("No billing records found")