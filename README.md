Armenian Voice AI bank supporter
Project Architecture
Scraping - Firecrawl Cloud
STT(Speech to Text) - Groq STT
Orchestration: LangChain serves as the framework to connect the vector database, embedding models, and the LLM.
Vector Database: ChromaDB (stored in back/rag/chroma_db) acts as the long-term memory, storing bank documents as high-dimensional vectors for semantic search.
Embeddings: HuggingFace (all-MiniLM-L6-v2) is used to convert text into numerical embeddings. This model runs entirely locally on the CPU.
LLM (Brain): Ollama (Llama 3) processes the retrieved context and the user's query to synthesize a natural response in Armenian.
TTS(Text to Speech) - Deepgram TTS

requirements

pip install langchain-huggingface langchain-community langchain-text-splitters chromadb sentence-transformers
pip install firecrawl-py
pip install livekit-plugins-deepgram livekit-plugins-groq groq python-dotenv
Docker Desktop (WSL)
Livekit Server
Ollama
https://ollama.com/download/windows
all-MiniLM-L6-v2 pytorch_model.bin

https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/tree/main
