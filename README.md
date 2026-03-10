# pdf-intelligence-rag

[![CI/CD Pipeline](https://github.com/yourusername/pdf-intelligence-rag/actions/workflows/main.yml/badge.svg)](https://github.com/yourusername/pdf-intelligence-rag/actions)

An automated RAG (Retrieval-Augmented Generation) engine designed for high-accuracy document intelligence.

## 🚀 Overview
This project implements a scalable pipeline to transform static PDF libraries into a searchable, interactive knowledge base. Unlike simple wrappers, this engine focuses on **retrieval accuracy** and **automated evaluation**.

## 🛠️ Tech Stack
- **Orchestration:** LangChain
- **API Framework:** FastAPI
- **Vector Store:** FAISS (Local) / Pinecone (Cloud)
- **Frontend:** Streamlit
- **DevOps:** Docker, GitHub Actions, Pytest

## 📈 Key Features
- **Automated Ingestion:** Watcher-based PDF indexing.
- **Thought Tracing:** Full callback logging for LLM reasoning steps.
- **Evaluation Suite:** Automated faithfulness and relevancy testing via `pytest`.

## 🚦 Getting Started
1. Clone the repo.
2. Run `docker-compose up`.
3. Access the API at `localhost:8000`.