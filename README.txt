Overview
This project is a voice-based AI assistant for Armenian banking services. It allows users to speak with an AI agent and receive spoken answers based on real banking data.
The system uses Retrieval-Augmented Generation (RAG) together with a Large Language Model (LLM) to generate accurate and context-based responses.
Features
Speech-to-Text (STT) using Groq Whisper
Text-to-Speech (TTS) using Deepgram
Large Language Model (LLM) using LLaMA 3
Voice communication via LiveKit
RAG with Chroma vector database
Web scraping using Firecrawl

Project Structure
bankagent/

  back/
    rag/
      chroma_db/ (vector database)
      ingest.py (data processing and embeddings)
    scrapers/
      build_db.py (scrapes bank websites)
  config/
    banksconfig.json (bank URLs configuration)
  data/
    banks.json (collected data)
  livekit/
    main.py (voice AI agent)
    docker-compose.yml
    livekit.yaml
    all-MiniLM-L6-v2 (embedding model)

How It Works

build_db.py scrapes banking websites and saves data into banks.json
ingest.py processes the data and creates embeddings
Data is stored in ChromaDB
main.py runs the voice AI agent
User speaks → speech is converted to text (STT)
Relevant information is retrieved from the database (RAG)
LLM (LLaMA 3 via Groq) generates an answer using retrieved context
Answer is converted back to speech (TTS)

=
The project uses a Large Language Model (LLaMA 3).
The model does not answer freely — it is restricted to use only the retrieved context from the vector database.
For using you must install Ollama https://ollama.com/download
and download llama3 latest version


Requirements
Python 3.10+
Docker
Python libraries:
langchain
langchain-community
langchain-core
langchain-text-splitters
langchain-huggingface
chromadb
sentence-transformers
firecrawl-py
livekit
livekit-agents
deepgram-sdk
groq
python-dotenv
silero

Installation


Create virtual environment

python -m venv venv

Activate environment

Windows:
venv\Scripts\activate

Install necessary dependencies(Requirements)

Setup
Set environment variables:
GROQ_API_KEY=your_key
DEEPGRAM_API_KEY=your_key
LIVEKIT_URL=http://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=devsecret

Run the Project

Start LiveKit
Start Ollama(llama3)
cd livekit
docker-compose up

Scrape data

python back/scrapers/build_db.py

Build vector database

python back/rag/ingest.py

Run the agent

python livekit/main.py

Limitations

The assistant only answers questions about:
Credits
Deposits
Branch locations
Responses depend only on available data
