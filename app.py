import streamlit as st
import requests
import os

st.set_page_config(page_title="PDF Intelligence", layout="wide")
st.title("📄 PDF Intelligence RAG Engine")

backend_url = os.getenv("BACKEND_URL", "http://backend:8000")

# --- Sidebar Status ---
st.sidebar.header("System Status")
if st.sidebar.button("Check Connection"):
    try:
        response = requests.get(f"{backend_url}/health")
        if response.status_code == 200:
            st.sidebar.success("✅ Backend Connected")
        else:
            st.sidebar.error("⚠️ Backend Error")
    except:
        st.sidebar.error("❌ Connection Failed")

# --- Main UI ---
st.write("Upload a document to begin the indexing process.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    if st.button("Process & Index PDF"):
        with st.spinner("Analyzing document..."):
            # Prepare the file to be sent via POST request
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            try:
                # We'll create this /upload endpoint in the next step
                response = requests.post(f"{backend_url}/upload", files=files)
                if response.status_code == 200:
                    st.success(f"Successfully indexed: {uploaded_file.name}")
                    st.json(response.json()) # Let's see what the backend found
                else:
                    st.error("Failed to process PDF.")
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")