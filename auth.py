import streamlit as st
import pandas as pd
import os

USER_FILE = "data/users.csv"

def initialize():
    if not os.path.exists(USER_FILE):
        df = pd.DataFrame([{
            "username": "admin",
            "password": "admin123"
        }])
        df.to_csv(USER_FILE, index=False)

def login_page():
    initialize()

    st.title("Hospital Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        df = pd.read_csv(USER_FILE)
        user = df[
            (df["username"] == username) &
            (df["password"] == password)
        ]

        if len(user) > 0:
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")