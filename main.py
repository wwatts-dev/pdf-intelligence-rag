import os
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from pypdf import PdfReader
from groq import Groq
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()

app = FastAPI(title="PDF Intelligence RAG Engine - Groq Edition")

# Initialize the Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.get("/")
async def root():
    return {"status": "online", "engine": "Groq Llama-3"}

@app.get("/test-ai")
async def test_ai():
    try:
        # Using the Llama 3 8B model for a lightning-fast test
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": "Say 'Hello, your Groq brain is connected!'"}
            ],
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ... (keep your existing Groq and app initialization) ...
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        # Read the file bytes into memory
        contents = await file.read()
        pdf_stream = io.BytesIO(contents)
        
        # Extract text using pypdf
        reader = PdfReader(pdf_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # For now, we'll just return the metadata and a snippet of text
        # Next, we will send this 'text' to FAISS for vector storage!
        return {
            "filename": file.filename,
            "page_count": len(reader.pages),
            "preview": text[:200] + "..." if text else "No text found"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")