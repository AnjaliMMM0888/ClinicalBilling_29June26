import streamlit as st
import pandas as pd

BILLING_FILE = "data/billing.csv"
ICD_FILE = "data/icd_master.csv"


def dashboard():
    st.title("📊 Revenue Dashboard")

    df = pd.read_csv(BILLING_FILE)
    icd = pd.read_csv(ICD_FILE)

    # Merge billing with ICD master
    merged = df.merge(icd, on="icd_code", how="left")

    # Safety check (VERY IMPORTANT)
    if merged.empty:
        st.warning("No billing data available")
        return

    # -----------------------
    # KPIs
    # -----------------------
    total_revenue = merged["total"].sum()
    total_bills = len(merged)
    avg_bill = merged["total"].mean()

    st.metric("Total Revenue", f"₹ {total_revenue:,.2f}")
    st.metric("Total Bills", total_bills)
    st.metric("Average Bill", f"₹ {avg_bill:,.2f}")

    # -----------------------
    # Revenue by ICD
    # -----------------------
    st.subheader("Revenue by ICD Code")
    icd_revenue = merged.groupby("icd_code")["total"].sum()
    st.bar_chart(icd_revenue)

    # -----------------------
    # Revenue by Disease
    # -----------------------
    st.subheader("Revenue by Disease (Description)")
    disease_revenue = merged.groupby("description")["total"].sum()
    st.bar_chart(disease_revenue)

    # -----------------------
    # Revenue by Category
    # -----------------------
    st.subheader("Revenue by Category")
    category_revenue = merged.groupby("category")["total"].sum()
    st.bar_chart(category_revenue)

    # -----------------------
    # Raw Data
    # -----------------------
    st.subheader("Billing Data (Joined)")
    st.dataframe(merged)