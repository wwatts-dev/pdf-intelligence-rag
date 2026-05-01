# pdf-intelligence-rag

[![CI/CD Pipeline](https://github.com/wwatts-dev/pdf-intelligence-rag/actions/workflows/main.yml/badge.svg)](https://github.com/wwatts-dev/pdf-intelligence-rag/actions)

An automated RAG (Retrieval-Augmented Generation) engine designed for high-accuracy document intelligence.

## 🚀 Overview
This project implements a scalable **RAG (Retrieval-Augmented Generation)** pipeline to transform static PDF libraries into a searchable, interactive knowledge base. Architected as a bridge between **Scalable Backend Infrastructure** and **Modern AI Orchestration**, this engine goes beyond simple wrappers to focus on **conversational continuity** and **architectural hygiene**.

By leveraging **LangChain** and **FastAPI**, the system solves the technical challenges of stateful AI interactions, ensuring that complex document queries are handled with high precision and local embedding optimization.

* **Hybrid AI Architecture**: Leverages **Groq** for high-speed **LLM inference** and local **HuggingFace** embeddings for secure, private data processing.
* **Performance-Optimized Infrastructure**: Architected to manage heavy **Model Weights** and Docker VHDX files to secondary storage (e.g., "M: drive"), demonstrating an understanding of system-level resource management. (**Note**: Fully compatible with single-drive configurations.)
* **Containerized Environment**: Fully orchestrated via **Docker** to ensure reproducible builds across different development environments.

## 📸 Demo Preview
![Screenshot of multi-turn chat summarizing and comparing BLS employment data](images/pdf-intelligence-rag-demo.png)

## 💻 Tech Stack
- **AI Orchestration**: LangChain (RAG, Memory, Chain-of-Thought)
- **Inference & Models**: Groq (Llama 3 / Mixtral), HuggingFace Transformers (Local Embeddings)
- **Vector Database**: FAISS (High-Performance Semantic Search)
- **Backend & API**: FastAPI (Asynchronous Python)
- **Frontend**: Streamlit (Conversational AI UI)
- **DevOps & QA**: Docker, GitHub Actions, Pytest (Automated Evaluation)

## 📈 Key Features
- **Stateful Conversational AI**: Manages multi-turn dialogues via session-based UUIDs, resolving ambiguous follow-up queries. (e.g., _"Was it higher than the month before?"_).
- **Contextual Query Expansion (NLU)**: Utilizes an LLM-driven standalone query generator to maintain **Natural Language Understanding** and retrieval relevance across chat history.
- **Automated RAG Evaluation**: Integrated `pytest` framework that validates **faithfulness, relevancy, and the stateful logic** to ensure high-precision Generative AI responses.
- **Chain-of-Thought Tracing**: Provides full callback logging for transparency into the LLM’s reasoning steps during the retrieval process.
- **On-Demand Vector Ingestion**: Streamlit-based UI for real-time PDF parsing, semantic chunking, and FAISS vector index creation.

---

## 🚦 Quick Start
1. **Clone**: `git clone https://github.com/wwatts-dev/pdf-intelligence-rag.git`
2. **Env**: Add `GROQ_API_KEY` to a `.env` file _with a generated Groq API key_.
3. **Run**: `docker-compose up --build`
4. **Open**: `localhost:8501`

---

## ⚙️ Detailed Setup Guide

### 1. Prerequisites
* **Git**: Required to clone the source code. Install the `Git-2.53.0.2-64-bit.exe` version (or newer) from the [official Git repository](https://github.com/git-for-windows/git/releases/tag/v2.53.0.windows.2).

> [!Tip]
> _To verify installation of Git, you can always open PowerShell and run `git --version` to confirm it is installed correctly._

* **Docker Desktop**: Required to run the containerized application stack. Download the AMD64 version (for Windows PCs) or one of the other versions that corresponds with your OS from the [official Docker site](https://www.docker.com/).
> [!Note]
> _If installing Docker Desktop for the first time, and asked to choose between installing WSL (Windows Subsystem for Linux) or Hyper-V, choosing WSL 2 is the most 'modern' option recommended for the best experience. Since Docker containers are inherently Linux-based, WSL allows you to run Linux-native tools (like Bash and git) alongside Windows applications such as Visual Studio Code._

> [!Tip]
> _Docker Desktop is always 'hidden' at the bottom of your system task tray on Windows-- even when pressing the 'X' icon to close and exit the application. However, to free up system resources on your computer when Docker isn't being used you must right-click on the icon in your system tray and select 'Quit Docker Desktop' to properly exit the application._

* **Groq API Key**: Required for the inference engine. Obtain a free key from the [Groq Console](https://console.groq.com/keys).
> [!Note]
> _You must sign into or create a Groq account to obtain your Groq API Key._

> [!Tip]
> _You may also use your GitHub account to sign into Groq to get your Groq API Key (instead of creating a separate account for Groq)._

* **Internet Connectivity**: Required for initialization and query processing.
> [!Important]
> An active internet connection is mandatory for this project for two reasons:
> 1. **Model Ingestion**: On the first launch, the backend must download approximately 500MB of `sentence-transformers` embedding models from HuggingFace to your local machine.
> 2. **Cloud Inference**: This project utilizes the **Groq API** to generate responses. While document processing happens locally, the final answer generation is handled via Groq's high-speed cloud infrastructure.

### 2. Installation & Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/wwatts-dev/pdf-intelligence-rag.git
   cd pdf-intelligence-rag
   ```
> [!Important]
> _You'll need to run the git clone command using PowerShell or a similar command-line shell._

> [!Note]
> _The above git clone command will install the project to the current directory your command-line shell is working from (the default directory is usually something similar to `C:\Users\your-name` when you first launch PowerShell each time). While basic command-line knowledge is assumed, you'll need to use a command such as `cd` to navigate to a different directory if you wish for the pdf-intelligence-rag project to be installed there instead._

> [!Tip]
> _I recommend taking a look at Geeksforgeeks.org to learn about [directory operation commands](https://www.geeksforgeeks.org/linux-unix/cd-command-in-linux-with-examples/) such as `cd`, or to see an organized list of many [helpful shell commands](https://www.geeksforgeeks.org/linux-unix/linux-commands-cheat-sheet/)._

2. **Configure Environment (`.env` file contents)**:
    ```env
    GROQ_API_KEY=your_key_here
    ```
> [!Note]
> _If you're editing the source code, the `.env` file is already ignored by Git within this project to ensure your keys remain private._

3. **Launch the Stack**:
    ```bash
    docker-compose up --build
    ```

### 3. Usage
* **Frontend UI**: Access at `localhost:8501` in your local web browser.
* **API Documentation**: Access at `localhost:8000/docs` in your local web browser.
> [!Tip]
> _To re-launch the project later, launch Docker Desktop and press the 'play' button over the pdf-intelligence-rag container. Then open your browser and go to `localhost:8501` to access the UI for the pdf-intelligence-rag project. (Pressing the square 'stop' button shuts down the container and prevents access to `localhost:8501` within your browser.)_

---

## 🛠️ Troubleshooting

### 🔑 Missing API Credentials
If you receive a `Backend Error: Internal Server Error: Connection error` error when pressing the **Process PDF** button, it is likely due to an issue with a missing or invalid setup with your Groq API key.
* **The Fix**: Ensure your `.env` file contains `GROQ_API_KEY=your_key_here`.
> [!Important]
> _The application requires a valid Groq API key to generate responses. If you haven't already created a Groq account you'll need to login or create one to access the Groq console to obtain your Groq API key necessary to run this project._

### ⚠️ Connection Error (Errno 111)
If you encounter a `Connection refused` error when clicking **Process PDF**, it is likely due to a service startup race condition.

* **The Cause**: The Frontend (Streamlit) starts instantly, but the Backend (FastAPI) must download and load ~500MB of HuggingFace embedding models before it can accept requests.
* **The Fix**: Wait approximately 60 seconds after running `docker-compose up`. Check your terminal logs; when you see `Uvicorn running on http://0.0.0.0:8000`, the system is ready.

### 🌐 Docker Networking (For Developers)
If the Frontend cannot reach the Backend inside Docker, ensure your environment variables use the service name `backend` rather than `localhost`.

* **Correct**: `http://backend:8000/query`
* **Incorrect**: `http://localhost:8000/query`
> [!Important]
> _If you're editing the source code or network settings, remember that the containers talk to each other using their names (`backend`), not `localhost`. In Docker, `localhost` refers to the container itself, not other services in the stack._

### 🔍 Log Retrieval
To verify if the backend has finished initializing or to debug crashes between sessions, you can check the historical service logs using the following commands in your terminal:
* **View Logs** (View the last few lines of logs):    
    ```bash
    docker-compose logs backend
    ```
* **Export for Review** (Export full logs to a file for analysis):
    ```bash
    docker-compose logs backend > backend_debug_log.txt
    ```
