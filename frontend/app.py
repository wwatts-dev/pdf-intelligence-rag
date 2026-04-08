import streamlit as st
import requests
import os
import uuid  # Added for session management

# Use the environment variable defined in docker-compose
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="PDF Intelligence RAG", layout="wide")
st.title("📄 PDF Intelligence RAG")

# --- SESSION STATE INITIALIZATION ---
# 1. Generate a unique ID for this user session if it doesn't exist
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 2. Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: Upload ---
with st.sidebar:
    st.header("Upload Document...")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if st.button("Process PDF"):
        if uploaded_file:
            with st.spinner("Analyzing PDF..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{BACKEND_URL}/upload", files=files)
                if response.status_code == 200:
                    st.success("PDF processed and indexed!")
                else:
                    st.error(f"Error: {response.json().get('detail')}")
    
    st.divider()
    # Updated Clear Memory to reset both the UI and the unique session ID
    if st.button("Clear Memory", type="primary"):
        try:
            response = requests.delete(f"{BACKEND_URL}/clear")
            if response.status_code == 200:
                st.session_state.messages = [] 
                st.session_state.session_id = str(uuid.uuid4()) # New ID for a fresh start
                st.success("Memory cleared!")
                st.rerun()
            else:
                st.error("Failed to clear backend memory.")
        except Exception as e:
            st.error(f"Connection Error: {str(e)}")

# --- Main Interface: Chat ---
st.subheader("Chat with your PDF")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask a question about your document..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # CRITICAL UPDATE: Sending both question AND session_id
                payload = {
                    "question": prompt,
                    "session_id": st.session_state.session_id
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/query", 
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer")
                    sources = data.get("sources", [])
                    
                    # Optional: Access the standalone_query to see how the AI rephrased the follow-up
                    # print(f"AI Search Query: {data.get('standalone_query')}")

                    st.markdown(answer)

                    if sources:
                        unique_sources = list(set(sources))
                        st.caption(f"Sources: {', '.join(unique_sources)}")

                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = response.json().get("detail", "Unknown error")
                    st.error(f"Backend Error: {error_msg}")
            except Exception as e:
                st.error(f"Connection Error: {str(e)}")