# RAG Service for document retrieval
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# --- Configuration ---
KNOWLEDGE_BASE_DIR = 'knowledge_base'
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
TOP_K_DOCS = 3  # Number of relevant documents to retrieve

# --- Globals ---
app = FastAPI()
vector_store = None

# --- Pydantic Models ---
class RetrieveRequest(BaseModel):
    query: str

class RetrieveResponse(BaseModel):
    context: str

# --- RAG Core Logic ---
def initialize_rag():
    """
    Loads documents, creates embeddings, and builds the FAISS vector store.
    This function is called once on application startup.
    """
    global vector_store
    print("Initializing RAG service...")
    
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        print(f"Knowledge base directory '{KNOWLEDGE_BASE_DIR}' not found. RAG will be inactive.")
        return

    try:
        # Load documents from the directory
        loader = DirectoryLoader(KNOWLEDGE_BASE_DIR, glob="**/*.md", loader_cls=TextLoader, show_progress=True)
        documents = loader.load()

        if not documents:
            print("No documents found in the knowledge base. RAG will be inactive.")
            return

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = text_splitter.split_documents(documents)
        print(f"Loaded and split {len(documents)} documents into {len(docs)} chunks.")

        # Create embeddings
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

        # Create FAISS vector store from documents
        print("Creating FAISS vector store...")
        vector_store = FAISS.from_documents(docs, embeddings)
        print("RAG service initialization complete.")

    except Exception as e:
        print(f"Error during RAG initialization: {e}")
        # vector_store will remain None, and the service will be inactive

# --- FastAPI Events ---
@app.on_event("startup")
async def startup_event():
    initialize_rag()

# --- FastAPI Endpoints ---
@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_documents(request: RetrieveRequest):
    """
    Retrieves relevant document chunks for a given query.
    """
    if vector_store is None:
        raise HTTPException(status_code=503, detail="RAG service is not available or failed to initialize.")
    
    try:
        # Search the vector store for relevant documents
        retriever = vector_store.as_retriever(search_kwargs={"k": TOP_K_DOCS})
        relevant_docs = retriever.get_relevant_documents(request.query)
        
        # Combine the content of the retrieved documents
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        return RetrieveResponse(context=context)
    except Exception as e:
        print(f"Error during document retrieval: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents.")

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify service status.
    """
    if vector_store is None:
        return {"status": "inactive", "message": "RAG service initialized but no vector store available."}
    return {"status": "ok"}

if __name__ == '__main__':
    import uvicorn
    # This allows running the service directly for testing
    uvicorn.run('rag_service:app', host='0.0.0.0', port=8003, reload=True)
