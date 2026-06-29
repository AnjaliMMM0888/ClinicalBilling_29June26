import streamlit as st
from auth import login_page
from patient import patient_registration, scan_barcode
from billing import billing_page
from analytics import dashboard
from pdf_generator import discharge_summary

st.set_page_config(page_title="Hospital ICD Billing App", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    st.sidebar.title("Menu")
    choice = st.sidebar.radio(
        "Select",
        [
            "Patient Registration",
            "Barcode Scan",
            "Billing",
            "Discharge Summary",
            "Dashboard"
        ]
    )

    if choice == "Patient Registration":
        patient_registration()

    elif choice == "Barcode Scan":
        scan_barcode()

    elif choice == "Billing":
        billing_page()

    elif choice == "Discharge Summary":
        discharge_summary()

    elif choice == "Dashboard":
        dashboard()