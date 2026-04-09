# pdf-intelligence-rag

[![CI/CD Pipeline](https://github.com/wwatts-dev/pdf-intelligence-rag/actions/workflows/main.yml/badge.svg)](https://github.com/wwatts-dev/pdf-intelligence-rag/actions)

An automated RAG (Retrieval-Augmented Generation) engine designed for high-accuracy document intelligence.

## 🚀 Overview
This project implements a scalable pipeline to transform static PDF libraries into a searchable, interactive knowledge base. Unlike simple RAG wrappers, this engine focuses on **conversational continuity** and **architectural hygiene**, ensuring that complex document queries are handled with high precision and stateful awareness.

* **Hybrid architecture**: Leverages **Groq** for high-speed response generation and local **HuggingFace** embeddings for private data processing.
* **Performance-First Infrastructure**: Architected to offload heavy AI model weights and Docker VHDX files to secondary storage (such as "M: drive"), optimizing system drive longevity. (**Note**: This app will also work exactly the same way on devices without a secondary drive.)
* **Docker** is required to run this project.

## 🛠️ Tech Stack
- **Orchestration:** LangChain
- **API Framework:** FastAPI
- **Vector Store:** FAISS (High-Performance Local)
- **Frontend:** Streamlit
- **DevOps:** Docker, GitHub Actions, Pytest

## 📈 Key Features
- **Stateful Conversational Memory:** Manages multi-turn dialogues via session-based UUIDs, enabling the system to resolve ambiguous follow-up questions. (e.g., "Was it higher than the month before?").
- **Contextual Query Re-writing:** Utilizes an LLM-driven standalone query generator to maintain retrieval relevance across chat history.
- **Automated Evaluation Suite:** Integrated `pytest` framework that validates faithfulness, relevancy, and the stateful logic of the conversational flow.
- **Thought Tracing:** Provides full callback logging for transparency into the LLM’s reasoning steps during the RAG process.
- **On-Demand Ingestion:** Streamlit-based UI for seamless document uploads and FAISS vector index creation.

## 🚦 Getting Started
1. Clone the repo.
2. Run `docker-compose up`.
3. Access the **Frontend UI** at `localhost:8501`.
4. Access the **API Documentation** at `localhost:8000/docs`.