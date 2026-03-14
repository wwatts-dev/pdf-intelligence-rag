import os
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader
from pydantic import BaseModel

# --- RAG & AI IMPORTS ---
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Create a simple schema for the request body
class QueryRequest(BaseModel):
    question: str

# Load variables from .env
load_dotenv()

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
        # Ensure the index directory exists on the M: drive via the mount
        if not os.path.exists("faiss_index"):
            os.makedirs("faiss_index")

        # 1. Extract Text from PDF
        contents = await file.read()
        pdf_stream = io.BytesIO(contents)
        reader = PdfReader(pdf_stream)
        
        raw_text = ""
        for page in reader.pages:
            text_content = page.extract_text()
            if text_content:
                raw_text += text_content

        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="The PDF appears to be empty or contains only images.")

        # 2. Chunking (Splitting text into 1000-character pieces)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=100
        )
        chunks = text_splitter.split_text(raw_text)

        # 3. Vector Storage (Turning text into mathematical coordinates)
        # This saves the 'Memory' into a local folder called 'faiss_index'
        vector_store = FAISS.from_texts(chunks, embeddings)
        vector_store.save_local("faiss_index")

        return {
            "filename": file.filename,
            "chunks_created": len(chunks),
            "engine": "HuggingFace Local",
            "status": "Vector Store Created Successfully"
        }
        
    except Exception as e:
        # Provide more specific error feedback
        raise HTTPException(status_code=500, detail=f"RAG Processing Error: {str(e)}")

@app.post("/query")
async def query_pdf(request: QueryRequest):
    try:
        # 1. Verification: Check if the index exists on the M: drive
        # Inside the container, this is simply the local folder mapped via volumes
        index_path = "faiss_index"
        if not os.path.exists(index_path):
            raise HTTPException(
                status_code=400, 
                detail="No PDF index found. Please upload a PDF first to initialize the vector store."
            )
        
        # 2. Load the Vector Store
        # We use allow_dangerous_deserialization=True because we created the file ourselves
        vector_store = FAISS.load_local(
            index_path, 
            embeddings, 
            allow_dangerous_deserialization=True
        )

        # 3. Similarity Search
        # Find the top 3 most relevant chunks of text from your PDF
        docs = vector_store.similarity_search(request.question, k=3)
        context = "\n".join([doc.page_content for doc in docs])

        # 4. Generate Answer via Groq
        # We provide the AI with the 'Context' and ask it to answer the 'Question'
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