# Voice AI Banking Assistant for Armenian Banks

An interactive, voice-based AI assistant designed for Armenian banking services. Users can converse naturally with an AI agent using spoken Armenian/English and receive accurate real-time verbal answers grounded in scraped banking data using Retrieval-Augmented Generation (RAG).

---

## Overview

This application combines Speech-to-Text (STT), a Large Language Model (LLM), and Text-to-Speech (TTS) inside a low-latency voice pipeline powered by LiveKit. To prevent hallucinations, the model is strictly constrained to answer queries using context retrieved from a local vector database populated with scraped bank data.

---

## Features

- **Speech-to-Text (STT):** Powered by Groq Whisper for fast speech recognition.
- **Large Language Model (LLM):** LLaMA 3 running locally via Ollama or Groq API.
- **Text-to-Speech (TTS):** Natural voice responses using Deepgram.
- **Voice Communication:** Real-time WebRTC audio streaming via LiveKit.
- **RAG Architecture:** Vector retrieval powered by ChromaDB and sentence transformers (`all-MiniLM-L6-v2`).
- **Web Scraping:** Automated bank website scraping using Firecrawl.

---

## Project Structure

```text
bankagent/
├── back/
│   ├── rag/
│   │   ├── chroma_db/       # Chroma vector database storage
│   │   └── ingest.py        # Data processing, chunking, and embeddings creation
│   └── scrapers/
│       └── build_db.py      # Scrapes target bank websites
├── config/
│   └── banksconfig.json     # Configuration file containing target bank URLs
├── data/
│   └── banks.json           # Raw scraped data output
└── livekit/
    ├── main.py              # Voice AI agent runtime logic
    ├── docker-compose.yml   # LiveKit server orchestration
    ├── livekit.yaml         # LiveKit server configuration
    └── all-MiniLM-L6-v2/    # Local embedding model weights

```

---

## How It Works

```
[ User Speaks ] ──► STT (Groq Whisper)
                         │
                         ▼
             [ Context Search in ChromaDB ]
                         │
                         ▼
             [ Prompt + Context Sent to LLaMA 3 ]
                         │
                         ▼
[ Spoken Response ] ◄── TTS (Deepgram) ◄── [ LLM Response ]

```

1. **Scrape Data:** `build_db.py` uses Firecrawl to extract content from configured bank websites and saves it into `data/banks.json`.
2. **Build Embeddings:** `ingest.py` processes raw JSON data, converts it into vector embeddings using `all-MiniLM-L6-v2`, and stores it in `ChromaDB`.
3. **Voice Pipeline:** When a user speaks, LiveKit streams audio to Groq Whisper for STT.
4. **Contextual Generation:** The text prompt queries ChromaDB for relevant context. LLaMA 3 generates an answer strictly bound by that context.
5. **Speech Response:** Deepgram converts the text answer to audio and plays it back to the user via LiveKit.

---

## Prerequisites & Requirements

* **Python:** 3.10 or higher
* **Containerization:** Docker & Docker Compose
* **LLM Engine:** [Ollama](https://ollama.com/download) installed locally with the `llama3` model.

### Key Python Dependencies

* `langchain`, `langchain-community`, `langchain-core`, `langchain-text-splitters`, `langchain-huggingface`
* `chromadb` & `sentence-transformers`
* `livekit` & `livekit-agents`
* `firecrawl-py`
* `deepgram-sdk`
* `groq`
* `python-dotenv`
* `silero`

---

## Installation & Setup

### 1. Clone the Repository & Set Up Virtual Environment

```bash
git clone [https://github.com/your-username/bankagent.git](https://github.com/your-username/bankagent.git)
cd bankagent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

### 2. Set Up Local Ollama Model

Install [Ollama](https://ollama.com/download) and pull the latest LLaMA 3 model:

```bash
ollama pull llama3

```

### 3. Environment Variables

Create a `.env` file in the root directory and add your credentials:

```env
GROQ_API_KEY=your_groq_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
LIVEKIT_URL=[http://127.0.0.1:7880](http://127.0.0.1:7880)
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=devsecret

```

---

## Running the Project

### Step 1: Start LiveKit Server

Navigate to the `livekit` directory and bring up the Docker containers:

```bash
cd livekit
docker-compose up -d
cd ..

```

### Step 2: Scrape Banking Data

Run the scraper to collect banking information into `data/banks.json`:

```bash
python back/scrapers/build_db.py

```

### Step 3: Populate the Vector Database

Ingest the scraped data into ChromaDB:

```bash
python back/rag/ingest.py

```

### Step 4: Launch the Voice AI Agent

Start the agent loop to handle voice interactions:

```bash
python livekit/main.py

```

---

## Limitations

* **Domain Specificity:** The assistant is strictly restricted to retrieved knowledge. It will not answer general-knowledge queries outside the vector database.
* **Supported Data Scope:** Currently optimized for answering queries related to:
* Loan & Credit information
* Deposit accounts & interest rates
* Bank branch & ATM locations


* **Data Freshness:** Information relies on the frequency of `build_db.py` executions.

```

```
