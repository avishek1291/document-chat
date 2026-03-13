from transcript import DocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.retrievers import BaseRetriever
from config import DOCUMENT_MODE
import os
import json
import hashlib


embedding_model_name='sentence-transformers/all-MiniLM-L6-v2'
EMBEDDINGS_DB_PATH = './faiss_db'  # Directory to store FAISS index
METADATA_FILE = './faiss_db/document_metadata.json'  # Track uploaded documents

class Splitter():

    def split_text(self, text: str):
        """Split text into chunks."""
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        documents = text_splitter.create_documents([text])
        return documents


class Vectors():
    def __init__(self):
        self.embeddings_model = HuggingFaceEmbeddings(model_name=embedding_model_name)

    def _get_document_hash(self, text: str) -> str:
        """Generate SHA256 hash of document text."""
        return hashlib.sha256(text.encode()).hexdigest()

    def _load_metadata(self) -> dict:
        """Load document metadata from file."""
        if os.path.exists(METADATA_FILE):
            try:
                with open(METADATA_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_metadata(self, metadata: dict) -> None:
        """Save document metadata to file."""
        os.makedirs(EMBEDDINGS_DB_PATH, exist_ok=True)
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)

    def is_document_embedded(self, text: str, filename: str) -> tuple:
        """Check if document is already embedded.
        Returns: (is_embedded: bool, message: str)
        """
        doc_hash = self._get_document_hash(text)
        metadata = self._load_metadata()
        
        # Check if this exact document (by hash) already exists
        for stored_hash, doc_info in metadata.items():
            if stored_hash == doc_hash:
                return True, f"✅ Document already embedded: {doc_info['filename']}"
        
        return False, None

    def generate_embeddings(self, documents):
        """Generate embeddings from documents."""
        generated_embeddings = self.embeddings_model.embed_documents([doc.page_content for doc in documents])
        return [self.embeddings_model, generated_embeddings, documents]

    def create_db_from_documents(self, documents, filename: str = "unknown"):
        """Create or update FAISS database from documents.
        
        Behavior controlled by DOCUMENT_MODE environment variable:
        - 'replace': Overwrites existing database (default)
        - 'merge': Adds to existing database
        """
        print(f"Generating embeddings (mode: {DOCUMENT_MODE})...")
        [self.embedding_model, generated_embeddings, docs] = self.generate_embeddings(documents)
        texts = [doc.page_content for doc in docs]
        text_embedding_pairs = list(zip(texts, generated_embeddings))
        
        # Check if merging with existing database
        if DOCUMENT_MODE == 'merge' and os.path.exists(EMBEDDINGS_DB_PATH):
            print(f"Loading existing database and merging...")
            try:
                db = FAISS.load_local(EMBEDDINGS_DB_PATH, self.embedding_model, allow_dangerous_deserialization=True)
                # Add new documents to existing database
                db.add_documents(documents)
                db.save_local(EMBEDDINGS_DB_PATH)
                print(f"FAISS database updated with new documents")
            except Exception as e:
                print(f"Failed to merge with existing DB, creating new one: {e}")
                db = FAISS.from_embeddings(text_embeddings=text_embedding_pairs, embedding=self.embedding_model)
                db.save_local(EMBEDDINGS_DB_PATH)
        else:
            # Replace mode: Create new database
            db = FAISS.from_embeddings(text_embeddings=text_embedding_pairs, embedding=self.embedding_model)
            db.save_local(EMBEDDINGS_DB_PATH)
            if DOCUMENT_MODE == 'replace':
                print(f"FAISS database saved (replacing previous documents)")
            else:
                print(f"FAISS database created")
        
        # Update metadata
        doc_hash = self._get_document_hash("".join(texts))
        metadata = self._load_metadata()
        metadata[doc_hash] = {
            "filename": filename,
            "chunks": len(docs),
            "text_length": sum(len(t) for t in texts)
        }
        self._save_metadata(metadata)
        
        return db

    def get_embedded_documents(self) -> list:
        """Get list of all embedded documents."""
        metadata = self._load_metadata()
        return [doc_info['filename'] for doc_info in metadata.values()]

    def get_retriver(self) -> BaseRetriever:
        """Get retriever from existing or new FAISS database."""
        
        # Check if embeddings database already exists
        if os.path.exists(EMBEDDINGS_DB_PATH):
            print(f"Loading existing embeddings from {EMBEDDINGS_DB_PATH}...")
            db = FAISS.load_local(EMBEDDINGS_DB_PATH, self.embeddings_model, allow_dangerous_deserialization=True)
        else:
            print("No existing FAISS database found. Please upload a document first.")
            return None
        
        return db.as_retriever(search_type='similarity', search_kwargs={"k": 4})



