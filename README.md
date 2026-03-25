# pdf-intelligence-rag

[![CI/CD Pipeline](https://github.com/wwatts-dev/pdf-intelligence-rag/actions/workflows/main.yml/badge.svg)](https://github.com/yourusername/pdf-intelligence-rag/actions)

An automated RAG (Retrieval-Augmented Generation) engine designed for high-accuracy document intelligence.

## 🚀 Overview
This project implements a scalable pipeline to transform static PDF libraries into a searchable, interactive knowledge base. Unlike simple wrappers, this engine focuses on **retrieval accuracy** and **automated evaluation**.
* **Hybrid architecture**: This project uses **Groq** for high-speed inference and local **HuggingFace** embeddings for cost-effective, private data processing.
* **Setup & Infrastructure**: This project is configured to offload heavy AI model weights and Docker VHDX files to secondary storage (M: drive) to maintain system drive performance. (**Note**: This app will also work on devices without a secondary drive.)
* **Docker** is required to run this project.

## 🛠️ Tech Stack
- **Orchestration:** LangChain
- **API Framework:** FastAPI
- **Vector Store:** FAISS (High-Performance Local)
- **Frontend:** Streamlit
- **DevOps:** Docker, GitHub Actions, Pytest

## 📈 Key Features
- **Automated Ingestion:** Streamlit-based On-demand Ingestion.
- **Thought Tracing:** Full callback logging for LLM reasoning steps.
- **Evaluation Suite:** Automated faithfulness and relevancy testing via `pytest`.

## 🚦 Getting Started
1. Clone the repo.
2. Run `docker-compose up`.
3. Access the **Frontend UI** at `localhost:8501`**.
4. Access the **API Documentation** at `localhost:8000/docs`.