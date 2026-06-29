import streamlit as st
import pandas as pd
import os
import qrcode

PATIENT_FILE = "data/patients.csv"

def initialize():
    if not os.path.exists(PATIENT_FILE):
        df = pd.DataFrame(columns=[
            "patient_id", "name", "age", "gender"
        ])
        df.to_csv(PATIENT_FILE, index=False)

def patient_registration():
    initialize()
    st.title("Patient Registration")

    patient_id = st.text_input("Patient ID")
    name = st.text_input("Name")
    age = st.number_input("Age", 1, 120)
    gender = st.selectbox("Gender", ["Male", "Female"])

    if st.button("Register"):
        df = pd.read_csv(PATIENT_FILE)

        new_row = {
            "patient_id": patient_id,
            "name": name,
            "age": age,
            "gender": gender
        }

        df = pd.concat([df, pd.DataFrame([new_row])])
        df.to_csv(PATIENT_FILE, index=False)

        barcode_data = f"{patient_id}|{name}|{age}|{gender}"
        img = qrcode.make(barcode_data)
        img.save(f"{patient_id}.png")

        st.success("Patient registered")
        st.image(f"{patient_id}.png")

def scan_barcode():
    st.title("Barcode Scan Simulation")
    barcode = st.text_input("Paste barcode content")
    if barcode:
        data = barcode.split("|")
        st.write("Patient ID:", data[0])
        st.write("Name:", data[1])
        st.write("Age:", data[2])
        st.write("Gender:", data[3])