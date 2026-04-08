import os
import io
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader
from pydantic import BaseModel
from langchain_core.documents import Document

# --- RAG & AI IMPORTS ---
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load variables from .env
load_dotenv()

# Define the path within the container's persistent volume
# This path is mapped within the local ./ai_cache folder via docker-compose
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")

# Create a simple schema for the request body
class QueryRequest(BaseModel):
    question: str
    session_id: str = "default_user"

app = FastAPI(title="PDF Intelligence RAG Engine - Groq Edition")

# --- GLOBAL INITIALIZATIONS ---
# Initialize Groq for the "Chatting" part
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Initialize HuggingFace for the "Memory/Math" part
# This is the 100% free local model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Global store for chat history
# session_id -> list of messages
# Note: Redis would be used instead of a 
#   dictonary here for larger prod environments
chat_histories = {}


@app.get("/")
async def root():
    return {"status": "online", "engine": "Groq + HuggingFace"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# --- PDF UPLOAD & VECTOR INDEXING ---
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        # 1. Extract Text and Create Document Objects
        contents = await file.read()
        pdf_stream = io.BytesIO(contents)
        reader = PdfReader(pdf_stream)
        
        # We will store LangChain 'Document' objects instead of just strings
        raw_documents = []
        
        for i, page in enumerate(reader.pages):
            text_content = page.extract_text()
            if text_content:
                # Attach the filename as 'source' metadata
                # Also track the page number for extra detail
                doc = Document(
                    page_content=text_content,
                    metadata={
                        "source": file.filename, 
                        "page": i + 1
                    }
                )
                raw_documents.append(doc)

        if not raw_documents:
            raise HTTPException(status_code=400, detail="The PDF appears to be empty or contains only images.")

        # 2. Chunking (Splitting Documents instead of raw text)
        # Using split_documents ensures the metadata (source filename) 
        # is copied over to every single smaller chunk.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=100
        )
        final_chunks = text_splitter.split_documents(raw_documents)

        # 3. Vector Storage
        # The 'Memory' from .from_documents() contains the text
        # PLUS the source information.
        vector_store = FAISS.from_documents(final_chunks, embeddings)
        
        # Use your helper to save to the persistent volume (M: drive)
        save_vector_store(vector_store)

        return {
            "filename": file.filename,
            "chunks_created": len(final_chunks),
            "engine": "HuggingFace Local",
            "status": "Vector Store Persistent Created Successfully"
        }
        
    except Exception as e:
        print(f"Upload Error Trace: {str(e)}") # Log the error to your Docker terminal
        raise HTTPException(status_code=500, detail=f"RAG Processing Error: {str(e)}")

@app.post("/query")
async def query_pdf(request: QueryRequest):
    try:
        # --- SESSION & MEMORY MANAGEMENT ---
        # Access the "Memory" for this specific session. 
        # This allows the backend to handle multiple users simultaneously.
        history = get_session_history(request.session_id)
        
        # --- CONTEXTUAL RE-WRITING ---
        # This is the "Intelligence" step. If there is history, we ask the LLM 
        # to clarify follow-up questions (e.g., "Is that high?") into standalone search terms.
        standalone_question = request.question
        history_str = ""
        
        if history:
            # We provide the AI with the last 5 exchanges to help it reason about intent
            history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-5:]])
            rewrite_prompt = (
                f"Given the following conversation history and a follow-up question, "
                f"rephrase the follow-up question to be a standalone question that can be searched.\n\n"
                f"History:\n{history_str}\n\n"
                f"Follow-up: {request.question}\n"
                f"Standalone Question:"
            )
            rewrite_resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": rewrite_prompt}]
            )
            standalone_question = rewrite_resp.choices[0].message.content

        # --- RETRIEVAL ---
        # Use the helper to load the index from the persistent mapped volume.
        vector_store = load_vector_store(embeddings)
        if not vector_store:
            raise HTTPException(
                status_code=400, 
                detail="No PDF index found. Please upload a PDF first."
            )

        # Similarity Search: Find the top 3 most relevant chunks of text from your PDF.
        # Note: We search using the 'standalone_question' to ensure the search is accurate.
        docs = vector_store.similarity_search(standalone_question, k=3)
        pdf_context = "\n".join([doc.page_content for doc in docs])

        # --- THOUGHT TRACING ---
        # This allows you to see exactly what was retrieved in the Docker terminal
        print(f"--- STANDALONE QUERY ---\n{standalone_question}")
        print(f"--- RETRIEVED CONTEXT ---\n{pdf_context}\n------------------------")

        # --- FINAL GENERATION ---
        # Provide the AI with the 'PDF Context', the 'Chat History', 
        # and the current question to generate a grounded, natural response.
        final_prompt = (
            f"You are a helpful assistant. Use the PDF context and the chat history to answer.\n\n"
            f"PDF Context:\n{pdf_context}\n\n"
            f"Chat History:\n{history_str if history_str else 'No prior history.'}\n\n"
            f"User's Question: {request.question}\n\n"
            f"Answer:"
        )
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": final_prompt}]
        )
        answer = completion.choices[0].message.content

        # --- MEMORY UPDATE ---
        # Store the exchange as simple dictionaries to keep session history manageable.
        # We limit this to the last 10 messages to maintain a relevant context window.
        history.append({"role": "user", "content": request.question})
        history.append({"role": "assistant", "content": answer})
        chat_histories[request.session_id] = history[-10:]

        return {
            "answer": answer,
            "sources": list(set([doc.metadata.get("source", "Unknown") for doc in docs])),
            "standalone_query": standalone_question
        }

    except Exception as e:
        print(f"Error during query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.delete("/clear")
async def clear_index():
    """Deletes the persistent vector store index."""
    try:
        if os.path.exists(INDEX_PATH):
            shutil.rmtree(INDEX_PATH)
            return {"status": "success", "message": "Vector store cleared successfully."}
        return {"status": "info", "message": "No index found to clear."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear index: {str(e)}")

# --- PERSISTENT VECTOR STORAGE ---
def save_vector_store(vector_store):
    # This saves the index to the mapped ai_cache volume
    vector_store.save_local(INDEX_PATH)

def load_vector_store(embeddings):
    if os.path.exists(INDEX_PATH):
        # Load the existing index from the volume
        return FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    return None

# --- IN-MEMORY STORE ---
def get_session_history(session_id: str):
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    return chat_histories[session_id]