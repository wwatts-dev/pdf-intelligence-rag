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

# Load variables from .env
load_dotenv()

# Define the path within the container's persistent volume
# This path is mapped within the local ./ai_cache folder via docker-compose
INDEX_PATH = "/root/.cache/huggingface/faiss_index"

# Create a simple schema for the request body
class QueryRequest(BaseModel):
    question: str

app = FastAPI(title="PDF Intelligence RAG Engine - Groq Edition")

# --- GLOBAL INITIALIZATIONS ---
# Initialize Groq for the "Chatting" part
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Initialize HuggingFace for the "Memory/Math" part
# This is the 100% free local model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

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
        # 1. Use the helper to load from the persistent M: drive volume
        vector_store = load_vector_store(embeddings)

        if not vector_store:
            raise HTTPException(
                status_code=400, 
                detail="No PDF index found. Please upload a PDF first."
            )

        # 2. Similarity Search
        # Find the top 3 most relevant chunks of text from your PDF
        docs = vector_store.similarity_search(request.question, k=3)
        context = "\n".join([doc.page_content for doc in docs])

        # --- THOUGHT TRACING ---
        # This allows you to see exactly what was retrieved in the terminal
        print(f"--- RETRIEVED CONTEXT ---\n{context}\n------------------------")

        # 3. Generate Answer via Groq
        # Provide the AI with the 'Context' and ask it to answer the 'Question'
        prompt = (
            f"Use the following pieces of context to answer the question at the end.\n"
            f"If you don't know the answer based on the context, just say you don't know.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {request.question}\n\n"
            f"Answer:"
        )
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "answer": completion.choices[0].message.content,
            "sources": [doc.metadata.get("source", "Unknown") for doc in docs]
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