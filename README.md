# IRCC RAG Agent

This project implements a Retrieval-Augmented Generation (RAG) agent focused on Canadian Immigration, Refugees and Citizenship (IRCC) data. It includes data scraping, embedding generation, a vector database store, and a query interface.

## Project Structure

The repository is organized as follows:

- **notebook/**: Jupyter notebooks for the agent pipeline.
    - `scrap.ipynb` / `scrap_1.ipynb`: Data scraping scripts to fetch IRCC content.
    - `clean_embedding.ipynb`: Preprocessing and cleaning of scraped data for embedding.
    - `rag.ipynb` / `rag_1.ipynb`:Main RAG implementation (retrieval and generation).
    - `data.parquet`: Compressed dataset file (if used).
- **notebook/data/**: Raw JSON data files scraped from IRCC sources, categorized by topic (e.g., `immigrate-canada`, `study-canada`, `visit-canada`). These serve as the knowledge base.
- **notebook/vector_db/**: (Local only) Persistent storage for the Chroma vector database. *Note: The vector database binaries are excluded from version control.*

## Getting Started

1.  **Dependencies**: Ensure you have the necessary Python libraries installed (e.g., `langchain`, `chromadb`, `pandas`, `notebook`, `openai` or your LLM provider).
2.  **Environment**: Set up your environment variables (e.g., `OPENAI_API_KEY`) if running the RAG notebooks.
3.  **Data**: The `notebook/data/` folder contains the JSON source documents.
4.  **Running**: Start with the notebooks in `notebook/` to inspect the scraping logic or run the RAG query agent.

## Usage

- run `notebook/rag.ipynb` to interact with the agent.
