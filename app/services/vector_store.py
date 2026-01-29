"""Vector store service for RAG-based content retrieval"""
import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
import hashlib
from pathlib import Path

from app.core import settings


class VectorStoreService:
    """Manages vector embeddings and semantic search for NYVO content"""
    
    COLLECTION_NAME = "nyvo_insurance_content"
    
    def __init__(self):
        # Initialize ChromaDB with persistence
        os.makedirs(settings.chroma_persist_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )
        
        # Get or create collection with OpenAI embeddings
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"description": "NYVO Insurance educational content"}
        )
    
    def _generate_doc_id(self, content: str, source: str) -> str:
        """Generate unique document ID"""
        return hashlib.md5(f"{source}:{content[:100]}".encode()).hexdigest()
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ) -> None:
        """Add documents to the vector store"""
        if ids is None:
            ids = [
                self._generate_doc_id(doc, meta.get("source", "unknown"))
                for doc, meta in zip(documents, metadatas)
            ]
        
        # Add in batches to avoid memory issues
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_metas = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            
            self.collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Dict:
        """Search for relevant documents"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_metadata
        )
        
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else []
        }
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        return {
            "name": self.COLLECTION_NAME,
            "count": self.collection.count()
        }
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection"""
        self.client.delete_collection(self.COLLECTION_NAME)
        self.collection = self.client.create_collection(
            name=self.COLLECTION_NAME,
            metadata={"description": "NYVO Insurance educational content"}
        )


class ContentIngestionService:
    """Service to ingest NYVO content library into vector store"""
    
    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store
        self.content_path = Path(settings.nyvo_content_path)
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                if break_point > chunk_size * 0.7:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if len(c) > 50]
    
    def _extract_text_from_file(self, file_path: Path) -> str:
        """Extract text from various file formats"""
        suffix = file_path.suffix.lower()
        
        if suffix in ['.txt', '.md']:
            return file_path.read_text(encoding='utf-8')
        
        elif suffix == '.pdf':
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(file_path))
                return "\n".join(page.extract_text() for page in reader.pages)
            except Exception as e:
                print(f"Error reading PDF {file_path}: {e}")
                return ""
        
        elif suffix == '.docx':
            try:
                from docx import Document
                doc = Document(str(file_path))
                return "\n".join(para.text for para in doc.paragraphs)
            except Exception as e:
                print(f"Error reading DOCX {file_path}: {e}")
                return ""
        
        return ""
    
    def _categorize_content(self, file_path: Path, content: str) -> Dict:
        """Categorize content based on file path and content"""
        path_str = str(file_path).lower()
        
        category = "general"
        insurance_type = None
        
        if "health" in path_str:
            category = "health_insurance"
            insurance_type = "health"
        elif "term" in path_str or "life" in path_str:
            category = "term_insurance"
            insurance_type = "term_life"
        elif "motor" in path_str or "car" in path_str or "vehicle" in path_str:
            category = "motor_insurance"
            insurance_type = "motor"
        elif "claim" in path_str:
            category = "claims"
        elif "regulation" in path_str or "irdai" in path_str:
            category = "regulations"
        elif "faq" in path_str or "basics" in path_str:
            category = "basics"
        
        return {
            "source": str(file_path),
            "category": category,
            "insurance_type": insurance_type,
            "file_name": file_path.name
        }
    
    def ingest_content_library(self) -> Dict:
        """Ingest all content from the NYVO content library"""
        if not self.content_path.exists():
            os.makedirs(self.content_path, exist_ok=True)
            return {"status": "error", "message": "Content directory is empty"}
        
        all_documents = []
        all_metadatas = []
        files_processed = 0
        
        # Supported extensions
        extensions = ['.txt', '.md', '.pdf', '.docx']
        
        for ext in extensions:
            for file_path in self.content_path.rglob(f"*{ext}"):
                text = self._extract_text_from_file(file_path)
                if not text:
                    continue
                
                chunks = self._chunk_text(text)
                base_metadata = self._categorize_content(file_path, text)
                
                for i, chunk in enumerate(chunks):
                    all_documents.append(chunk)
                    metadata = {**base_metadata, "chunk_index": i}
                    all_metadatas.append(metadata)
                
                files_processed += 1
        
        if all_documents:
            self.vector_store.add_documents(all_documents, all_metadatas)
        
        return {
            "status": "success",
            "files_processed": files_processed,
            "chunks_created": len(all_documents)
        }


# Singleton instances
vector_store = VectorStoreService()
content_ingestion = ContentIngestionService(vector_store)
