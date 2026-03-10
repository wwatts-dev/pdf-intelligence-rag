from fastapi import FastAPI

app = FastAPI(title="PDF Intelligence RAG Engine")

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "AI RAG Engine is ready for document ingestion.",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}